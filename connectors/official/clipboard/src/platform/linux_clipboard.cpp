#include "linux_clipboard.hpp"
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xfixes.h>
#include <iostream>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <thread>
#include <functional>
#include <atomic>

class LinuxClipboard::Impl {
public:
    Display* display;
    Window window;
    Atom clipboard;
    Atom utf8;
    Atom targets;
    Window lastClipboardOwner;
    std::thread monitorThread;
    std::atomic<bool> monitoring{false};
    std::function<void()> changeCallback;
    bool eventDrivenMode;
    bool xfixesAvailable;
    int xfixesEventBase;
    int xfixesErrorBase;
    
    Impl() : display(nullptr), window(0), lastClipboardOwner(None), 
             eventDrivenMode(false), xfixesAvailable(false),
             xfixesEventBase(0), xfixesErrorBase(0) {
        display = XOpenDisplay(nullptr);
        if (display) {
            int screen = DefaultScreen(display);
            window = XCreateSimpleWindow(display, RootWindow(display, screen),
                                       0, 0, 1, 1, 0, 0, 0);
            
            clipboard = XInternAtom(display, "CLIPBOARD", False);
            utf8 = XInternAtom(display, "UTF8_STRING", False);
            targets = XInternAtom(display, "TARGETS", False);
            
            // 检查XFixes扩展是否可用
            xfixesAvailable = XFixesQueryExtension(display, &xfixesEventBase, &xfixesErrorBase);
            
            lastClipboardOwner = XGetSelectionOwner(display, clipboard);
        }
    }
    
    ~Impl() {
        stopEventMonitoring();
        if (display) {
            if (window) {
                XDestroyWindow(display, window);
            }
            XCloseDisplay(display);
        }
    }
    
    bool setupEventDrivenMode() {
        if (!xfixesAvailable || !display) {
            return false;
        }
        
        // 使用根窗口来监听全局剪贴板事件
        Window rootWindow = DefaultRootWindow(display);
        
        // 注册监听CLIPBOARD选择变化事件
        XFixesSelectSelectionInput(display, rootWindow, clipboard,
                                   XFixesSetSelectionOwnerNotifyMask);
        
        // 也监听PRIMARY选择（Linux中的另一种剪贴板）
        Atom primary = XA_PRIMARY;
        XFixesSelectSelectionInput(display, rootWindow, primary,
                                   XFixesSetSelectionOwnerNotifyMask);
        
        XFlush(display);
        return true;
    }
    
    void cleanupEventDrivenMode() {
        if (xfixesAvailable && display) {
            Window rootWindow = DefaultRootWindow(display);
            XFixesSelectSelectionInput(display, rootWindow, clipboard, 0);
            XFixesSelectSelectionInput(display, rootWindow, XA_PRIMARY, 0);
            XFlush(display);
        }
    }
    
    void startEventMonitoring(std::function<void()> callback) {
        if (monitoring.load() || !display) return;
        
        changeCallback = callback;
        monitoring.store(true);
        
        // 尝试使用事件驱动模式
        eventDrivenMode = setupEventDrivenMode();
        
        monitorThread = std::thread([this]() {
            if (eventDrivenMode) {
                // 真正的事件驱动模式：阻塞等待XFixes事件
                XEvent event;
                while (monitoring.load()) {
                    // 使用XNextEvent阻塞等待事件 - 这是真正的事件驱动
                    if (XCheckMaskEvent(display, -1, &event)) {
                        if (event.type == xfixesEventBase + XFixesSelectionNotify) {
                            XFixesSelectionNotifyEvent* selEvent = 
                                reinterpret_cast<XFixesSelectionNotifyEvent*>(&event);
                            
                            // 响应CLIPBOARD或PRIMARY选择变化
                            if (selEvent->selection == clipboard || 
                                selEvent->selection == XA_PRIMARY) {
                                if (changeCallback) {
                                    changeCallback();
                                }
                            }
                        }
                    } else {
                        // 没有事件时短暂休眠，避免空跑
                        std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    }
                }
            } else {
                // 降级到轮询模式
                int idleCount = 0;
                
                while (monitoring.load()) {
                    Window currentOwner = XGetSelectionOwner(display, clipboard);
                    if (currentOwner != lastClipboardOwner) {
                        lastClipboardOwner = currentOwner;
                        idleCount = 0;
                        
                        if (changeCallback) {
                            changeCallback();
                        }
                    } else {
                        idleCount++;
                    }
                    
                    // 自适应间隔
                    int interval = (idleCount < 10) ? 50 : 
                                  (idleCount < 100) ? 200 : 
                                  (idleCount < 600) ? 1000 : 2000;
                    
                    std::this_thread::sleep_for(std::chrono::milliseconds(interval));
                }
            }
        });
    }
    
    void stopEventMonitoring() {
        monitoring.store(false);
        
        if (eventDrivenMode) {
            cleanupEventDrivenMode();
        }
        
        if (monitorThread.joinable()) {
            monitorThread.join();
        }
        
        eventDrivenMode = false;
    }
};

LinuxClipboard::LinuxClipboard() : pImpl(std::make_unique<Impl>()) {}

LinuxClipboard::~LinuxClipboard() = default;

std::string LinuxClipboard::getText() {
    if (!pImpl->display) {
        return "";
    }
    
    // Request clipboard content
    XConvertSelection(pImpl->display, pImpl->clipboard, pImpl->utf8,
                     pImpl->clipboard, pImpl->window, CurrentTime);
    XFlush(pImpl->display);
    
    // Wait for selection notify event
    XEvent event;
    bool received = false;
    for (int i = 0; i < 50; ++i) { // 5 second timeout
        if (XCheckTypedWindowEvent(pImpl->display, pImpl->window, SelectionNotify, &event)) {
            received = true;
            break;
        }
        usleep(100000); // 100ms
    }
    
    if (!received) {
        return "";
    }
    
    if (event.xselection.property == None) {
        return "";
    }
    
    // Get the data
    Atom actual_type;
    int actual_format;
    unsigned long bytes_after;
    unsigned long length;
    unsigned char* data = nullptr;
    
    int result = XGetWindowProperty(pImpl->display, pImpl->window, pImpl->clipboard,
                                   0, ~0L, False, AnyPropertyType,
                                   &actual_type, &actual_format, &length,
                                   &bytes_after, &data);
    
    std::string text;
    if (result == Success && data != nullptr) {
        text = std::string(reinterpret_cast<char*>(data), length);
        XFree(data);
    }
    
    XDeleteProperty(pImpl->display, pImpl->window, pImpl->clipboard);
    
    return text;
}

bool LinuxClipboard::setText(const std::string& text) {
    // For simplicity, this implementation only supports reading
    // Setting clipboard on X11 requires running an event loop
    // which is more complex for a background process
    return false;
}

void LinuxClipboard::startEventMonitoring(std::function<void()> callback) {
    pImpl->startEventMonitoring(callback);
}

void LinuxClipboard::stopEventMonitoring() {
    pImpl->stopEventMonitoring();
}

bool LinuxClipboard::isMonitoring() const {
    return pImpl->monitoring.load();
}