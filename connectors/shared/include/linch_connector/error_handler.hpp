#pragma once

#include <string>
#include <memory>
#include <functional>
#include <chrono>
#include <exception>
#include <map>

namespace linch_connector {

/**
 * 错误严重性级别 - 与Python版本保持一致
 */
enum class ErrorSeverity {
    LOW,        // 可忽略错误
    MEDIUM,     // 需要注意的错误
    HIGH,       // 严重错误，需要立即处理
    CRITICAL    // 致命错误，可能导致系统不稳定
};

/**
 * 错误分类 - 与Python版本保持一致
 */
enum class ErrorCategory {
    IPC_COMMUNICATION,
    DATABASE_OPERATION,
    STORAGE_OPERATION,
    SEARCH_OPERATION,
    EVENT_PROCESSING,
    MAINTENANCE_OPERATION,
    CONNECTOR_MANAGEMENT,
    CONNECTOR_DISCOVERY,
    FILE_SYSTEM,
    CONFIGURATION,
    SECURITY,
    NETWORK,
    SYSTEM_OPERATION,
    AI_PROCESSING,
    UNKNOWN
};

/**
 * 错误上下文信息
 */
struct ErrorContext {
    std::string function_name;
    std::string module_name;
    ErrorSeverity severity;
    ErrorCategory category;
    std::string user_message;
    std::string technical_details;
    std::string recovery_suggestions;
    
    ErrorContext(
        const std::string& func_name,
        const std::string& mod_name,
        ErrorSeverity sev,
        ErrorCategory cat,
        const std::string& user_msg = "",
        const std::string& tech_details = "",
        const std::string& recovery = ""
    ) : function_name(func_name),
        module_name(mod_name),
        severity(sev),
        category(cat),
        user_message(user_msg),
        technical_details(tech_details),
        recovery_suggestions(recovery) {}
};

/**
 * 标准化异常类
 */
class StandardizedException : public std::exception {
public:
    StandardizedException(
        const std::string& message,
        const ErrorContext& context,
        const std::exception* original = nullptr
    );
    
    const char* what() const noexcept override;
    const ErrorContext& getContext() const noexcept;
    const std::exception* getOriginalException() const noexcept;
    
private:
    std::string message_;
    ErrorContext context_;
    const std::exception* original_exception_;
};

/**
 * 处理后的错误信息 - 用于安全的IPC传输
 */
struct ProcessedError {
    std::string error_id;
    std::string code;
    std::string message;
    std::string user_message;
    bool is_recoverable;
    bool can_retry;
    int retry_after = 0;  // 重试延迟（秒）
    
    // 转换为安全的JSON字符串（用于IPC传输）
    std::string toSafeJson() const;
};

/**
 * 错误处理器 - 统一C++连接器的错误处理
 */
class ErrorHandler {
public:
    using RecoveryHandler = std::function<bool(const StandardizedException&)>;
    
    ErrorHandler();
    ~ErrorHandler();
    
    /**
     * 注册错误恢复处理器
     */
    void registerRecoveryHandler(ErrorCategory category, RecoveryHandler handler);
    
    /**
     * 处理错误
     */
    ProcessedError handleError(
        const std::exception& exception,
        const ErrorContext& context,
        bool attempt_recovery = false
    );
    
    /**
     * 记录错误日志
     */
    void logError(const StandardizedException& error);
    
    /**
     * 获取错误统计信息
     */
    std::map<std::string, int> getErrorStats() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
    
    std::string generateErrorCode(const std::exception& exception, const ErrorContext& context);
    std::string getUserMessage(const ErrorContext& context);
    bool isRecoverable(const ErrorContext& context);
    bool canRetry(const ErrorContext& context);
    int getRetryDelay(const ErrorContext& context);
};

/**
 * 获取全局错误处理器
 */
ErrorHandler& getErrorHandler();

/**
 * 错误严重性和分类的字符串转换函数
 */
std::string severityToString(ErrorSeverity severity);
std::string categoryToString(ErrorCategory category);

/**
 * 错误处理宏 - 简化错误处理代码
 */
#define HANDLE_CONNECTOR_ERROR(severity, category, user_msg, code_block) \
    try { \
        code_block \
    } catch (const std::exception& e) { \
        ErrorContext ctx(__FUNCTION__, __FILE__, severity, category, user_msg); \
        auto processed = getErrorHandler().handleError(e, ctx); \
        std::cerr << "[ERROR] " << processed.user_message << " (ID: " << processed.error_id << ")" << std::endl; \
        if (processed.can_retry) { \
            std::cerr << "[INFO] 可在 " << processed.retry_after << " 秒后重试" << std::endl; \
        } \
    }

/**
 * IPC错误处理宏
 */
#define HANDLE_IPC_ERROR(user_msg, code_block) \
    HANDLE_CONNECTOR_ERROR(ErrorSeverity::HIGH, ErrorCategory::IPC_COMMUNICATION, user_msg, code_block)

/**
 * 配置错误处理宏
 */
#define HANDLE_CONFIG_ERROR(user_msg, code_block) \
    HANDLE_CONNECTOR_ERROR(ErrorSeverity::HIGH, ErrorCategory::CONFIGURATION, user_msg, code_block)

/**
 * 文件系统错误处理宏
 */
#define HANDLE_FS_ERROR(user_msg, code_block) \
    HANDLE_CONNECTOR_ERROR(ErrorSeverity::MEDIUM, ErrorCategory::FILE_SYSTEM, user_msg, code_block)

} // namespace linch_connector