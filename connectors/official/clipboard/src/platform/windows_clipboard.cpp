#include "windows_clipboard.hpp"
#include <windows.h>
#include <iostream>
#include <thread>
#include <functional>
#include <atomic>

class WindowsClipboard::Impl {
private:
    static const UINT WM_CLIPBOARDUPDATE = 0x031D;
    static LRESULT CALLBACK windowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
        if (uMsg == WM_CLIPBOARDUPDATE) {
            Impl* self = reinterpret_cast<Impl*>(GetWindowLongPtr(hwnd, GWLP_USERDATA));
            if (self && self->changeCallback) {
                self->changeCallback();
            }
            return 0;
        }
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }

public:
    DWORD lastSequenceNumber;
    std::thread monitorThread;
    std::atomic<bool> monitoring{false};
    std::function<void()> changeCallback;
    HWND hiddenWindow;
    bool eventDrivenMode;
    
    Impl() : hiddenWindow(nullptr), eventDrivenMode(false) {
        lastSequenceNumber = GetClipboardSequenceNumber();
    }
    
    ~Impl() {
        stopEventMonitoring();
    }
    
    bool createHiddenWindow() {
        const char* className = "LinchMindClipboardWindow";
        
        WNDCLASS wc = {};
        wc.lpfnWndProc = windowProc;
        wc.hInstance = GetModuleHandle(nullptr);
        wc.lpszClassName = className;
        
        RegisterClass(&wc);
        
        hiddenWindow = CreateWindow(
            className, "LinchMindClipboard",
            0, 0, 0, 0, 0,
            HWND_MESSAGE, nullptr, GetModuleHandle(nullptr), nullptr
        );
        
        if (hiddenWindow) {
            SetWindowLongPtr(hiddenWindow, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(this));
            return AddClipboardFormatListener(hiddenWindow);
        }
        return false;
    }
    
    void destroyHiddenWindow() {
        if (hiddenWindow) {
            RemoveClipboardFormatListener(hiddenWindow);
            DestroyWindow(hiddenWindow);
            hiddenWindow = nullptr;
        }
    }
    
    void startEventMonitoring(std::function<void()> callback) {
        if (monitoring.load()) return;
        
        changeCallback = callback;
        monitoring.store(true);
        
        // 尝试使用事件驱动模式
        eventDrivenMode = createHiddenWindow();
        
        monitorThread = std::thread([this]() {
            if (eventDrivenMode) {
                // 事件驱动模式：运行消息循环
                MSG msg;
                while (monitoring.load()) {
                    BOOL result = GetMessage(&msg, hiddenWindow, 0, 0);
                    if (result > 0) {
                        TranslateMessage(&msg);
                        DispatchMessage(&msg);
                    } else if (result == 0) {
                        // WM_QUIT received
                        break;
                    }
                    // result < 0 means error, continue
                }
            } else {
                // 降级到轮询模式
                int idleCount = 0;
                
                while (monitoring.load()) {
                    DWORD currentSequenceNumber = GetClipboardSequenceNumber();
                    if (currentSequenceNumber != lastSequenceNumber) {
                        lastSequenceNumber = currentSequenceNumber;
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
                    
                    Sleep(interval);
                }
            }
        });
    }
    
    void stopEventMonitoring() {
        monitoring.store(false);
        
        if (eventDrivenMode && hiddenWindow) {
            PostMessage(hiddenWindow, WM_QUIT, 0, 0);
        }
        
        if (monitorThread.joinable()) {
            monitorThread.join();
        }
        
        destroyHiddenWindow();
        eventDrivenMode = false;
    }
};

WindowsClipboard::WindowsClipboard() : pImpl(std::make_unique<Impl>()) {}

WindowsClipboard::~WindowsClipboard() = default;

bool WindowsClipboard::openClipboard() {
    // Try to open clipboard with retry
    for (int i = 0; i < 10; ++i) {
        if (OpenClipboard(nullptr)) {
            return true;
        }
        Sleep(10);
    }
    return false;
}

void WindowsClipboard::closeClipboard() {
    CloseClipboard();
}

std::string WindowsClipboard::getText() {
    std::string result;
    
    if (!openClipboard()) {
        return result;
    }
    
    HANDLE hData = GetClipboardData(CF_UNICODETEXT);
    if (hData != nullptr) {
        wchar_t* pszText = static_cast<wchar_t*>(GlobalLock(hData));
        if (pszText != nullptr) {
            // Convert wide string to UTF-8
            int size_needed = WideCharToMultiByte(CP_UTF8, 0, pszText, -1, nullptr, 0, nullptr, nullptr);
            if (size_needed > 0) {
                std::string strTo(size_needed - 1, 0);
                WideCharToMultiByte(CP_UTF8, 0, pszText, -1, &strTo[0], size_needed, nullptr, nullptr);
                result = strTo;
            }
            GlobalUnlock(hData);
        }
    }
    
    closeClipboard();
    return result;
}

bool WindowsClipboard::setText(const std::string& text) {
    if (!openClipboard()) {
        return false;
    }
    
    EmptyClipboard();
    
    // Convert UTF-8 to wide string
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, nullptr, 0);
    if (size_needed == 0) {
        closeClipboard();
        return false;
    }
    
    HGLOBAL hGlob = GlobalAlloc(GMEM_MOVEABLE, size_needed * sizeof(wchar_t));
    if (hGlob == nullptr) {
        closeClipboard();
        return false;
    }
    
    wchar_t* pGlob = static_cast<wchar_t*>(GlobalLock(hGlob));
    MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, pGlob, size_needed);
    GlobalUnlock(hGlob);
    
    bool success = SetClipboardData(CF_UNICODETEXT, hGlob) != nullptr;
    closeClipboard();
    
    return success;
}

unsigned int WindowsClipboard::getSequenceNumber() {
    return GetClipboardSequenceNumber();
}

void WindowsClipboard::startEventMonitoring(std::function<void()> callback) {
    pImpl->startEventMonitoring(callback);
}

void WindowsClipboard::stopEventMonitoring() {
    pImpl->stopEventMonitoring();
}

bool WindowsClipboard::isMonitoring() const {
    return pImpl->monitoring.load();
}