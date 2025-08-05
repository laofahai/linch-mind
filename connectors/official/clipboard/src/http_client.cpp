#include "http_client.hpp"
#include <curl/curl.h>
#include <iostream>
#include <sstream>

// Callback function for curl to write response data
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    size_t totalSize = size * nmemb;
    userp->append((char*)contents, totalSize);
    return totalSize;
}

class HttpClient::Impl {
public:
    CURL* curl;
    struct curl_slist* headers;
    int timeout_seconds;

    Impl() : curl(nullptr), headers(nullptr), timeout_seconds(30) {
        curl_global_init(CURL_GLOBAL_DEFAULT);
        curl = curl_easy_init();
        
        if (curl) {
            // Set default options
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
            curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);
        }
    }

    ~Impl() {
        if (headers) {
            curl_slist_free_all(headers);
        }
        if (curl) {
            curl_easy_cleanup(curl);
        }
        curl_global_cleanup();
    }

    Response performRequest(const std::string& url, const std::string* postData = nullptr) {
        Response response;
        std::string responseBody;

        if (!curl) {
            response.statusCode = 500;
            response.body = "CURL initialization failed";
            return response;
        }

        // Set URL
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &responseBody);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);

        // Set headers if any
        if (headers) {
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        }

        // Configure for POST if data provided
        if (postData) {
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postData->c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, postData->length());
        } else {
            curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);
        }

        // Perform the request
        CURLcode res = curl_easy_perform(curl);
        
        if (res != CURLE_OK) {
            response.statusCode = 500;
            response.body = std::string("CURL error: ") + curl_easy_strerror(res);
            return response;
        }

        // Get response code
        long responseCode;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &responseCode);
        
        response.statusCode = static_cast<int>(responseCode);
        response.body = responseBody;

        return response;
    }
};

HttpClient::HttpClient() : pImpl(std::make_unique<Impl>()) {}

HttpClient::~HttpClient() = default;

HttpClient::Response HttpClient::get(const std::string& url) {
    return pImpl->performRequest(url);
}

HttpClient::Response HttpClient::post(const std::string& url, const std::string& jsonData) {
    return pImpl->performRequest(url, &jsonData);
}

void HttpClient::setTimeout(int timeout_seconds) {
    pImpl->timeout_seconds = timeout_seconds;
}

void HttpClient::addHeader(const std::string& key, const std::string& value) {
    std::string header = key + ": " + value;
    pImpl->headers = curl_slist_append(pImpl->headers, header.c_str());
}