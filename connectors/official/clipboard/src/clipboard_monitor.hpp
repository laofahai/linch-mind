#pragma once

#include <functional>
#include <memory>
#include <string>
#include <thread>
#include <atomic>

/**
 * Cross-platform clipboard monitoring interface
 * Provides unified access to system clipboard across Windows/macOS/Linux
 */
class ClipboardMonitor {
public:
    using ChangeCallback = std::function<void(const std::string&)>;

    ClipboardMonitor();
    ~ClipboardMonitor();

    /**
     * Start monitoring clipboard changes
     * @param callback Function to call when clipboard content changes
     * @param interval_ms Polling interval in milliseconds (default 1000)
     * @return true if monitoring started successfully
     */
    bool startMonitoring(ChangeCallback callback, int interval_ms = 1000);

    /**
     * Stop clipboard monitoring
     */
    void stopMonitoring();

    /**
     * Get current clipboard content
     * @return Current clipboard text content
     */
    std::string getCurrentContent();

    /**
     * Check if monitoring is currently active
     */
    bool isMonitoring() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
    
    std::atomic<bool> m_monitoring{false};
    std::thread m_monitorThread;
    ChangeCallback m_callback;
    std::string m_lastContent;
    int m_interval_ms{1000};

    void monitorLoop();
    std::string getClipboardText();
};