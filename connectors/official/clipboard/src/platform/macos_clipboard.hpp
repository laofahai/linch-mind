#pragma once

#include <string>
#include <functional>
#include <memory>

/**
 * macOS clipboard implementation using NSPasteboard
 * Now supports event-driven monitoring using changeCount
 */
class MacOSClipboard {
public:
    MacOSClipboard();
    ~MacOSClipboard();

    /**
     * Get current clipboard text content
     * @return Clipboard text content, empty string if no text available
     */
    std::string getText();

    /**
     * Set clipboard text content
     * @param text Text to set to clipboard
     * @return true if successful
     */
    bool setText(const std::string& text);

    /**
     * Get clipboard change count
     * Used to detect clipboard changes without polling content
     * @return Current change count
     */
    int getChangeCount();

    /**
     * Start event-driven clipboard monitoring
     * @param callback Function to call when clipboard changes
     */
    void startEventMonitoring(std::function<void()> callback);

    /**
     * Stop clipboard monitoring
     */
    void stopEventMonitoring();

    /**
     * Check if monitoring is currently active
     */
    bool isMonitoring() const;

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};