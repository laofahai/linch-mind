#pragma once

#include <string>
#include <map>
#include <memory>

namespace linch_connector {

/**
 * HTTP client wrapper around libcurl
 * Provides simple GET/POST operations for daemon communication
 */
class HttpClient {
public:
    struct Response {
        int statusCode;
        std::string body;
        std::map<std::string, std::string> headers;
        
        bool isSuccess() const { return statusCode >= 200 && statusCode < 300; }
    };

    HttpClient();
    ~HttpClient();

    /**
     * Perform HTTP GET request
     * @param url Target URL
     * @return Response object with status and content
     */
    Response get(const std::string& url);

    /**
     * Perform HTTP POST request with JSON data
     * @param url Target URL
     * @param jsonData JSON string to send in request body
     * @return Response object with status and content
     */
    Response post(const std::string& url, const std::string& jsonData);

    /**
     * Set request timeout in seconds
     * @param timeout_seconds Timeout value (default: 30)
     */
    void setTimeout(int timeout_seconds);

    /**
     * Add custom header to all requests
     * @param key Header name
     * @param value Header value
     */
    void addHeader(const std::string& key, const std::string& value);

private:
    class Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace linch_connector