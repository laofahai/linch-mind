#include "clipboard_monitor.hpp"
#include <chrono>
#include <iostream>

// Platform-specific implementations
#ifdef _WIN32
#include "platform/windows_clipboard.hpp"
#elif __APPLE__
#include "platform/macos_clipboard.hpp"
#else
#include "platform/linux_clipboard.hpp"
#endif

class ClipboardMonitor::Impl {
public:
#ifdef _WIN32
    WindowsClipboard clipboard;
#elif __APPLE__
    MacOSClipboard clipboard;
#else
    LinuxClipboard clipboard;
#endif

    std::function<void(const std::string&)> userCallback;
    std::string lastContent;

    void onClipboardChange() {
        try {
            std::string currentContent = clipboard.getText();
            
            if (currentContent != lastContent) {
                lastContent = currentContent;
                if (userCallback && !currentContent.empty()) {
                    userCallback(currentContent);
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Error handling clipboard change: " << e.what() << std::endl;
        }
    }
};

ClipboardMonitor::ClipboardMonitor() : pImpl(std::make_unique<Impl>()) {}

ClipboardMonitor::~ClipboardMonitor() {
    stopMonitoring();
}

bool ClipboardMonitor::startMonitoring(ChangeCallback callback, int interval_ms) {
    if (m_monitoring.load()) {
        return false; // Already monitoring
    }

    // Store user callback and get initial content
    pImpl->userCallback = callback;
    pImpl->lastContent = getCurrentContent();
    
    // Use event-driven monitoring instead of polling
    auto eventCallback = [this]() {
        pImpl->onClipboardChange();
    };
    
    m_monitoring.store(true);
    pImpl->clipboard.startEventMonitoring(eventCallback);
    
    std::cout << "📋 Started event-driven clipboard monitoring (optimized)" << std::endl;
    return true;
}

bool ClipboardMonitor::startMonitoring(ChangeCallback callback) {
    // Default to event-driven monitoring without interval
    return startMonitoring(callback, 0);
}

void ClipboardMonitor::stopMonitoring() {
    if (m_monitoring.load()) {
        pImpl->clipboard.stopEventMonitoring();
        m_monitoring.store(false);
        std::cout << "📋 Stopped event-driven clipboard monitoring" << std::endl;
    }
}

std::string ClipboardMonitor::getCurrentContent() {
    return getClipboardText();
}

bool ClipboardMonitor::isMonitoring() const {
    return m_monitoring.load() && pImpl->clipboard.isMonitoring();
}

std::string ClipboardMonitor::getClipboardText() {
    return pImpl->clipboard.getText();
}