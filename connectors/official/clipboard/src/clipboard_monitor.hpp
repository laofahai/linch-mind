#pragma once

#include <functional>
#include <memory>
#include <string>
#include <atomic>

/**
 * Cross-platform clipboard monitoring interface
 * Now uses event-driven monitoring instead of polling for optimal performance
 * Provides unified access to system clipboard across Windows/macOS/Linux
 */
class ClipboardMonitor {
public:
    using ChangeCallback = std::function<void(const std::string&)>;

    ClipboardMonitor();
    ~ClipboardMonitor();

    /**
     * Start event-driven clipboard monitoring (recommended)
     * @param callback Function to call when clipboard content changes
     * @return true if monitoring started successfully
     */
    bool startMonitoring(ChangeCallback callback);

    /**
     * Start clipboard monitoring with legacy polling support
     * @param callback Function to call when clipboard content changes
     * @param interval_ms Polling interval (ignored in event-driven mode)
     * @return true if monitoring started successfully
     */
    bool startMonitoring(ChangeCallback callback, int interval_ms);

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

    std::string getClipboardText();
};