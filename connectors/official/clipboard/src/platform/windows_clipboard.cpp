#include "windows_clipboard.hpp"
#include <windows.h>
#include <iostream>

WindowsClipboard::WindowsClipboard() {}

WindowsClipboard::~WindowsClipboard() {}

bool WindowsClipboard::openClipboard() {
    // Try to open clipboard with retry
    for (int i = 0; i < 10; ++i) {
        if (OpenClipboard(nullptr)) {
            return true;
        }
        Sleep(10);
    }
    return false;
}

void WindowsClipboard::closeClipboard() {
    CloseClipboard();
}

std::string WindowsClipboard::getText() {
    std::string result;
    
    if (!openClipboard()) {
        return result;
    }
    
    HANDLE hData = GetClipboardData(CF_UNICODETEXT);
    if (hData != nullptr) {
        wchar_t* pszText = static_cast<wchar_t*>(GlobalLock(hData));
        if (pszText != nullptr) {
            // Convert wide string to UTF-8
            int size_needed = WideCharToMultiByte(CP_UTF8, 0, pszText, -1, nullptr, 0, nullptr, nullptr);
            if (size_needed > 0) {
                std::string strTo(size_needed - 1, 0);
                WideCharToMultiByte(CP_UTF8, 0, pszText, -1, &strTo[0], size_needed, nullptr, nullptr);
                result = strTo;
            }
            GlobalUnlock(hData);
        }
    }
    
    closeClipboard();
    return result;
}

bool WindowsClipboard::setText(const std::string& text) {
    if (!openClipboard()) {
        return false;
    }
    
    EmptyClipboard();
    
    // Convert UTF-8 to wide string
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, nullptr, 0);
    if (size_needed == 0) {
        closeClipboard();
        return false;
    }
    
    HGLOBAL hGlob = GlobalAlloc(GMEM_MOVEABLE, size_needed * sizeof(wchar_t));
    if (hGlob == nullptr) {
        closeClipboard();
        return false;
    }
    
    wchar_t* pGlob = static_cast<wchar_t*>(GlobalLock(hGlob));
    MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, pGlob, size_needed);
    GlobalUnlock(hGlob);
    
    bool success = SetClipboardData(CF_UNICODETEXT, hGlob) != nullptr;
    closeClipboard();
    
    return success;
}

unsigned int WindowsClipboard::getSequenceNumber() {
    return GetClipboardSequenceNumber();
}