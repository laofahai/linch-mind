#pragma once

#include <string>

/**
 * Windows clipboard implementation using Win32 API
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

private:
    bool openClipboard();
    void closeClipboard();
};