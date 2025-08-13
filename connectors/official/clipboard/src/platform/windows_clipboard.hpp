#pragma once

#include <string>
#include <functional>
#include <memory>

/**
 * Windows clipboard implementation using Win32 API
 * Now supports event-driven monitoring using GetClipboardSequenceNumber
 */
class WindowsClipboard {
public:
    WindowsClipboard();
    ~WindowsClipboard();

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
     * Get clipboard sequence number
     * Used to detect clipboard changes
     * @return Current sequence number
     */
    unsigned int getSequenceNumber();

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
    
    bool openClipboard();
    void closeClipboard();
};