#pragma once

#include <string>

/**
 * macOS clipboard implementation using NSPasteboard
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

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};