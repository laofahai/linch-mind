#pragma once

#include <string>
#include <memory>

/**
 * Linux clipboard implementation using X11
 */
class LinuxClipboard {
public:
    LinuxClipboard();
    ~LinuxClipboard();

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

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};