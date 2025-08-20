#include "linch_connector/error_handler.hpp"
#include <iostream>
#include <sstream>
#include <chrono>
#include <random>
#include <iomanip>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace linch_connector {

// StandardizedException 实现
StandardizedException::StandardizedException(
    const std::string& message,
    const ErrorContext& context,
    const std::exception* original
) : message_(message), context_(context), original_exception_(original) {}

const char* StandardizedException::what() const noexcept {
    return message_.c_str();
}

const ErrorContext& StandardizedException::getContext() const noexcept {
    return context_;
}

const std::exception* StandardizedException::getOriginalException() const noexcept {
    return original_exception_;
}

// ProcessedError 实现
std::string ProcessedError::toSafeJson() const {
    json j = {
        {"error_id", error_id},
        {"code", code},
        {"message", user_message},  // 只返回用户友好消息
        {"is_recoverable", is_recoverable},
        {"can_retry", can_retry},
        {"retry_after", retry_after}
    };
    return j.dump();
}

// ErrorHandler::Impl 实现
class ErrorHandler::Impl {
public:
    std::map<ErrorCategory, RecoveryHandler> recovery_handlers;
    std::map<std::string, int> error_stats;
    
    std::string generateUniqueId() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(1000, 9999);
        
        std::ostringstream oss;
        oss << "ERR_" << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S")
            << "_" << std::setfill('0') << std::setw(3) << ms.count()
            << "_" << dis(gen);
        return oss.str();
    }
    
    void logStructuredError(const std::string& error_id, 
                           const std::exception& exception,
                           const ErrorContext& context) {
        // 结构化错误日志
        std::cerr << "\n🚨 " << severityToString(context.severity) << " ERROR [" << error_id << "]\n"
                  << "   Function: " << context.function_name << "\n"
                  << "   Module: " << context.module_name << "\n"
                  << "   Category: " << categoryToString(context.category) << "\n"
                  << "   Message: " << exception.what() << "\n";
        
        if (!context.user_message.empty()) {
            std::cerr << "   User Message: " << context.user_message << "\n";
        }
        
        if (!context.technical_details.empty()) {
            std::cerr << "   Technical Details: " << context.technical_details << "\n";
        }
        
        if (!context.recovery_suggestions.empty()) {
            std::cerr << "   Recovery Suggestions: " << context.recovery_suggestions << "\n";
        }
        
        std::cerr << std::endl;
    }
};

// ErrorHandler 实现
ErrorHandler::ErrorHandler() : pImpl(std::make_unique<Impl>()) {
    // 注册默认恢复处理器
    registerRecoveryHandler(ErrorCategory::IPC_COMMUNICATION, [](const StandardizedException& e) {
        std::cerr << "[RECOVERY] 尝试重新建立IPC连接..." << std::endl;
        // 实际恢复逻辑可以在这里实现
        return false; // 暂时返回false，表示恢复失败
    });
    
    registerRecoveryHandler(ErrorCategory::CONFIGURATION, [](const StandardizedException& e) {
        std::cerr << "[RECOVERY] 尝试重新加载配置..." << std::endl;
        return false;
    });
}

ErrorHandler::~ErrorHandler() = default;

void ErrorHandler::registerRecoveryHandler(ErrorCategory category, RecoveryHandler handler) {
    pImpl->recovery_handlers[category] = handler;
    std::cout << "[ErrorHandler] 已注册 " << categoryToString(category) << " 错误恢复处理器" << std::endl;
}

ProcessedError ErrorHandler::handleError(
    const std::exception& exception,
    const ErrorContext& context,
    bool attempt_recovery
) {
    // 生成唯一错误ID
    std::string error_id = pImpl->generateUniqueId();
    
    // 更新错误统计
    std::string stat_key = categoryToString(context.category) + "_" + severityToString(context.severity);
    pImpl->error_stats[stat_key]++;
    
    // 创建标准化异常
    StandardizedException std_exception(exception.what(), context, &exception);
    
    // 记录错误日志
    pImpl->logStructuredError(error_id, exception, context);
    
    // 尝试错误恢复
    bool recovery_successful = false;
    if (attempt_recovery && pImpl->recovery_handlers.find(context.category) != pImpl->recovery_handlers.end()) {
        try {
            recovery_successful = pImpl->recovery_handlers[context.category](std_exception);
            if (recovery_successful) {
                std::cerr << "✅ [RECOVERY] 错误恢复成功: " << context.function_name << std::endl;
            } else {
                std::cerr << "❌ [RECOVERY] 错误恢复失败: " << context.function_name << std::endl;
            }
        } catch (const std::exception& recovery_error) {
            std::cerr << "❌ [RECOVERY] 恢复过程中发生异常: " << recovery_error.what() << std::endl;
        }
    }
    
    // 创建处理后的错误信息
    ProcessedError processed = {
        .error_id = error_id,
        .code = generateErrorCode(exception, context),
        .message = exception.what(),  // 内部消息
        .user_message = getUserMessage(context),
        .is_recoverable = isRecoverable(context),
        .can_retry = canRetry(context),
        .retry_after = getRetryDelay(context)
    };
    
    return processed;
}

void ErrorHandler::logError(const StandardizedException& error) {
    pImpl->logStructuredError("MANUAL_LOG", error, error.getContext());
}

std::map<std::string, int> ErrorHandler::getErrorStats() const {
    return pImpl->error_stats;
}

std::string ErrorHandler::generateErrorCode(const std::exception& exception, const ErrorContext& context) {
    // 生成错误代码: CATEGORY_EXCEPTION_TYPE
    std::string category_str = categoryToString(context.category);
    std::string exception_type = typeid(exception).name();
    
    // 简化异常类型名
    size_t pos = exception_type.find_last_of(":");
    if (pos != std::string::npos) {
        exception_type = exception_type.substr(pos + 1);
    }
    
    return category_str + "_" + exception_type;
}

std::string ErrorHandler::getUserMessage(const ErrorContext& context) {
    if (!context.user_message.empty()) {
        return context.user_message;
    }
    
    // 默认用户友好消息
    switch (context.category) {
        case ErrorCategory::IPC_COMMUNICATION:
            return "连接出现问题，正在重试";
        case ErrorCategory::CONFIGURATION:
            return "配置错误，请检查设置";
        case ErrorCategory::CONNECTOR_MANAGEMENT:
            return "连接器操作失败";
        case ErrorCategory::FILE_SYSTEM:
            return "文件系统操作失败";
        case ErrorCategory::NETWORK:
            return "网络连接异常";
        case ErrorCategory::SECURITY:
            return "安全验证失败";
        default:
            return "操作失败，请稍后重试";
    }
}

bool ErrorHandler::isRecoverable(const ErrorContext& context) {
    switch (context.category) {
        case ErrorCategory::IPC_COMMUNICATION:
        case ErrorCategory::NETWORK:
        case ErrorCategory::DATABASE_OPERATION:
            return true;
        case ErrorCategory::CONFIGURATION:
        case ErrorCategory::SECURITY:
            return false;
        default:
            return true;
    }
}

bool ErrorHandler::canRetry(const ErrorContext& context) {
    switch (context.category) {
        case ErrorCategory::CONFIGURATION:
        case ErrorCategory::SECURITY:
            return false;
        default:
            return true;
    }
}

int ErrorHandler::getRetryDelay(const ErrorContext& context) {
    if (!canRetry(context)) {
        return 0;
    }
    
    switch (context.category) {
        case ErrorCategory::IPC_COMMUNICATION:
            return 1;
        case ErrorCategory::NETWORK:
            return 3;
        case ErrorCategory::DATABASE_OPERATION:
            return 2;
        default:
            return 5;
    }
}

// 全局错误处理器
static ErrorHandler global_error_handler;

ErrorHandler& getErrorHandler() {
    return global_error_handler;
}

// 工具函数实现
std::string severityToString(ErrorSeverity severity) {
    switch (severity) {
        case ErrorSeverity::LOW: return "LOW";
        case ErrorSeverity::MEDIUM: return "MEDIUM";
        case ErrorSeverity::HIGH: return "HIGH";
        case ErrorSeverity::CRITICAL: return "CRITICAL";
        default: return "UNKNOWN";
    }
}

std::string categoryToString(ErrorCategory category) {
    switch (category) {
        case ErrorCategory::IPC_COMMUNICATION: return "IPC_COMMUNICATION";
        case ErrorCategory::DATABASE_OPERATION: return "DATABASE_OPERATION";
        case ErrorCategory::STORAGE_OPERATION: return "STORAGE_OPERATION";
        case ErrorCategory::SEARCH_OPERATION: return "SEARCH_OPERATION";
        case ErrorCategory::EVENT_PROCESSING: return "EVENT_PROCESSING";
        case ErrorCategory::MAINTENANCE_OPERATION: return "MAINTENANCE_OPERATION";
        case ErrorCategory::CONNECTOR_MANAGEMENT: return "CONNECTOR_MANAGEMENT";
        case ErrorCategory::CONNECTOR_DISCOVERY: return "CONNECTOR_DISCOVERY";
        case ErrorCategory::FILE_SYSTEM: return "FILE_SYSTEM";
        case ErrorCategory::CONFIGURATION: return "CONFIGURATION";
        case ErrorCategory::SECURITY: return "SECURITY";
        case ErrorCategory::NETWORK: return "NETWORK";
        case ErrorCategory::SYSTEM_OPERATION: return "SYSTEM_OPERATION";
        case ErrorCategory::AI_PROCESSING: return "AI_PROCESSING";
        default: return "UNKNOWN";
    }
}

} // namespace linch_connector