#include "linux_clipboard.hpp"
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <iostream>
#include <vector>
#include <cstring>
#include <unistd.h>

class LinuxClipboard::Impl {
public:
    Display* display;
    Window window;
    Atom clipboard;
    Atom utf8;
    Atom targets;
    
    Impl() : display(nullptr), window(0) {
        display = XOpenDisplay(nullptr);
        if (display) {
            int screen = DefaultScreen(display);
            window = XCreateSimpleWindow(display, RootWindow(display, screen),
                                       0, 0, 1, 1, 0, 0, 0);
            
            clipboard = XInternAtom(display, "CLIPBOARD", False);
            utf8 = XInternAtom(display, "UTF8_STRING", False);
            targets = XInternAtom(display, "TARGETS", False);
        }
    }
    
    ~Impl() {
        if (display) {
            if (window) {
                XDestroyWindow(display, window);
            }
            XCloseDisplay(display);
        }
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