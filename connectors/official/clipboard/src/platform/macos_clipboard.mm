#include "macos_clipboard.hpp"
#import <Cocoa/Cocoa.h>
#include <memory>
#include <thread>
#include <functional>
#include <atomic>

@interface ClipboardObserver : NSObject
@property (assign) std::function<void()> callback;
- (void)pasteboardDidChange:(NSNotification*)notification;
@end

@implementation ClipboardObserver
- (void)pasteboardDidChange:(NSNotification*)notification {
    if (self.callback) {
        self.callback();
    }
}
@end

class MacOSClipboard::Impl {
public:
    NSPasteboard* pasteboard;
    NSInteger lastChangeCount;
    std::thread monitorThread;
    std::atomic<bool> monitoring{false};
    std::function<void()> changeCallback;
    ClipboardObserver* observer;
    bool eventDrivenMode;
    dispatch_source_t timerSource;
    
    Impl() : observer(nullptr), eventDrivenMode(false), timerSource(nullptr) {
        pasteboard = [NSPasteboard generalPasteboard];
        lastChangeCount = [pasteboard changeCount];
    }
    
    ~Impl() {
        stopEventMonitoring();
        if (observer) {
            [observer release];
        }
    }
    
    bool setupEventDrivenMode() {
        @autoreleasepool {
            observer = [[ClipboardObserver alloc] init];
            observer.callback = changeCallback;
            
            // macOS没有直接的剪贴板通知API
            // 使用Carbon Event Manager尝试监听系统剪贴板事件
            // 或者使用NSWorkspace通知来检测应用切换（可能伴随剪贴板变化）
            
            // 注册应用激活通知，这可能表示用户进行了复制操作
            [[NSNotificationCenter defaultCenter] 
                addObserver:observer
                   selector:@selector(pasteboardDidChange:)
                       name:NSApplicationDidBecomeActiveNotification
                     object:nil];
            
            [[NSNotificationCenter defaultCenter] 
                addObserver:observer
                   selector:@selector(pasteboardDidChange:)
                       name:NSApplicationDidResignActiveNotification
                     object:nil];
            
            // 由于macOS没有真正的剪贴板事件，我们必须承认这仍然需要轮询
            // 但可以使用更高效的kqueue来监听系统事件
            return false; // 返回false表示无法实现真正的事件驱动
        }
    }
    
    void cleanupEventDrivenMode() {
        @autoreleasepool {
            [[NSNotificationCenter defaultCenter] removeObserver:observer];
        }
        if (timerSource) {
            dispatch_source_cancel(timerSource);
            dispatch_release(timerSource);
            timerSource = nullptr;
        }
    }
    
    void startEventMonitoring(std::function<void()> callback) {
        if (monitoring.load()) return;
        
        changeCallback = callback;
        monitoring.store(true);
        
        // 尝试使用优化的事件驱动模式
        eventDrivenMode = setupEventDrivenMode();
        
        // macOS没有真正的事件驱动API，必须使用优化的轮询
        // 使用智能的自适应轮询策略
        monitorThread = std::thread([this]() {
            int idleCount = 0;
            
            while (monitoring.load()) {
                @autoreleasepool {
                    NSInteger currentChangeCount = [pasteboard changeCount];
                    if (currentChangeCount != lastChangeCount) {
                        lastChangeCount = currentChangeCount;
                        idleCount = 0;
                        
                        if (changeCallback) {
                            changeCallback();
                        }
                    } else {
                        idleCount++;
                    }
                }
                
                // 智能自适应间隔：根据活跃度调整检查频率
                // 活跃时快速响应，空闲时节省资源
                int interval = (idleCount < 5) ? 20 :      // 前5次快速检查：20ms
                              (idleCount < 20) ? 100 :     // 后15次中等：100ms  
                              (idleCount < 120) ? 500 :    // 2分钟内：500ms
                              1000;                        // 长期空闲：1秒
                
                std::this_thread::sleep_for(std::chrono::milliseconds(interval));
            }
        });
    }
    
    void stopEventMonitoring() {
        monitoring.store(false);
        
        cleanupEventDrivenMode();
        
        if (monitorThread.joinable()) {
            monitorThread.join();
        }
        
        eventDrivenMode = false;
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

void MacOSClipboard::startEventMonitoring(std::function<void()> callback) {
    pImpl->startEventMonitoring(callback);
}

void MacOSClipboard::stopEventMonitoring() {
    pImpl->stopEventMonitoring();
}

bool MacOSClipboard::isMonitoring() const {
    return pImpl->monitoring.load();
}