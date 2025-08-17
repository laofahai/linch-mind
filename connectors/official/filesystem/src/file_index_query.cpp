#include "file_index_query.hpp"

#ifdef __APPLE__
#include "macos_mdquery_provider.hpp"
#endif

namespace linch_connector {

std::unique_ptr<IFileIndexQuery> createFileIndexQuery() {
#ifdef __APPLE__
    auto provider = std::make_unique<MacOSMdqueryProvider>();
    if (provider->isAvailable()) {
        return std::move(provider);
    }
#endif

#ifdef _WIN32
    // TODO: 实现Windows文件搜索API
    // return std::make_unique<WindowsFileSearchProvider>();
#endif

#ifdef __linux__
    // TODO: 实现Linux locate提供者
    // return std::make_unique<LinuxLocateProvider>();
#endif

    return nullptr;
}

} // namespace linch_connector