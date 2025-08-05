#include "macos_clipboard.hpp"
#import <Cocoa/Cocoa.h>
#include <memory>

class MacOSClipboard::Impl {
public:
    NSPasteboard* pasteboard;
    
    Impl() {
        pasteboard = [NSPasteboard generalPasteboard];
    }
};

MacOSClipboard::MacOSClipboard() : pImpl(std::make_unique<Impl>()) {}

MacOSClipboard::~MacOSClipboard() = default;

std::string MacOSClipboard::getText() {
    @autoreleasepool {
        NSString* content = [pImpl->pasteboard stringForType:NSPasteboardTypeString];
        if (content) {
            return std::string([content UTF8String]);
        }
        return "";
    }
}

bool MacOSClipboard::setText(const std::string& text) {
    @autoreleasepool {
        [pImpl->pasteboard clearContents];
        NSString* nsText = [NSString stringWithUTF8String:text.c_str()];
        return [pImpl->pasteboard setString:nsText forType:NSPasteboardTypeString];
    }
}

int MacOSClipboard::getChangeCount() {
    return static_cast<int>([pImpl->pasteboard changeCount]);
}