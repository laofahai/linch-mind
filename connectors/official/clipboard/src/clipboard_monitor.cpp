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
};

ClipboardMonitor::ClipboardMonitor() : pImpl(std::make_unique<Impl>()) {}

ClipboardMonitor::~ClipboardMonitor() {
    stopMonitoring();
}

bool ClipboardMonitor::startMonitoring(ChangeCallback callback, int interval_ms) {
    if (m_monitoring.load()) {
        return false; // Already monitoring
    }

    m_callback = callback;
    m_interval_ms = interval_ms;
    
    // Get initial content
    m_lastContent = getCurrentContent();
    
    m_monitoring.store(true);
    m_monitorThread = std::thread(&ClipboardMonitor::monitorLoop, this);
    
    return true;
}

void ClipboardMonitor::stopMonitoring() {
    m_monitoring.store(false);
    if (m_monitorThread.joinable()) {
        m_monitorThread.join();
    }
}

std::string ClipboardMonitor::getCurrentContent() {
    return getClipboardText();
}

bool ClipboardMonitor::isMonitoring() const {
    return m_monitoring.load();
}

void ClipboardMonitor::monitorLoop() {
    while (m_monitoring.load()) {
        try {
            std::string currentContent = getClipboardText();
            
            if (currentContent != m_lastContent) {
                m_lastContent = currentContent;
                if (m_callback && !currentContent.empty()) {
                    m_callback(currentContent);
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Error in clipboard monitoring: " << e.what() << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(m_interval_ms));
    }
}

std::string ClipboardMonitor::getClipboardText() {
#ifdef _WIN32
    return pImpl->clipboard.getText();
#elif __APPLE__
    return pImpl->clipboard.getText();
#else
    return pImpl->clipboard.getText();
#endif
}