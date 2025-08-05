#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <getopt.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Version {
    int major, minor, patch;
    
    Version(const std::string& version_str) {
        std::istringstream iss(version_str);
        std::string token;
        std::vector<int> parts;
        
        while (std::getline(iss, token, '.')) {
            parts.push_back(std::stoi(token));
        }
        
        major = parts.size() > 0 ? parts[0] : 0;
        minor = parts.size() > 1 ? parts[1] : 0;
        patch = parts.size() > 2 ? parts[2] : 1;
    }
    
    void bump(const std::string& type) {
        if (type == "major") {
            major++;
            minor = 0;
            patch = 0;
        } else if (type == "minor") {
            minor++;
            patch = 0;
        } else { // patch
            patch++;
        }
    }
    
    std::string toString() const {
        return std::to_string(major) + "." + std::to_string(minor) + "." + std::to_string(patch);
    }
};

std::string bumpVersion(const std::string& config_file, const std::string& bump_type) {
    // Read JSON file
    std::ifstream file(config_file);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + config_file);
    }
    
    json data;
    file >> data;
    file.close();
    
    // Get current version
    std::string current_version = data.value("version", "0.0.1");
    Version version(current_version);
    
    // Bump version
    version.bump(bump_type);
    std::string new_version = version.toString();
    
    std::cout << "Bumping " << config_file << ": " << current_version << " -> " << new_version << std::endl;
    
    // Update JSON
    data["version"] = new_version;
    
    // Write back to file
    std::ofstream outfile(config_file);
    outfile << data.dump(2) << std::endl;
    outfile.close();
    
    std::cout << "✅ Updated " << data["id"] << " to version " << new_version << std::endl;
    return new_version;
}

void printUsage(const char* program_name) {
    std::cout << "Usage: " << program_name << " <config_file> [--bump <type>]" << std::endl;
    std::cout << "  --bump: major, minor, or patch (default: patch)" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string config_file;
    std::string bump_type = "patch";
    
    // Parse command line arguments
    static struct option long_options[] = {
        {"bump", required_argument, 0, 'b'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    int option_index = 0;
    int c;
    
    while ((c = getopt_long(argc, argv, "b:h", long_options, &option_index)) != -1) {
        switch (c) {
            case 'b':
                bump_type = optarg;
                if (bump_type != "major" && bump_type != "minor" && bump_type != "patch") {
                    std::cerr << "Invalid bump type: " << bump_type << std::endl;
                    return 1;
                }
                break;
            case 'h':
                printUsage(argv[0]);
                return 0;
            default:
                printUsage(argv[0]);
                return 1;
        }
    }
    
    if (optind >= argc) {
        std::cerr << "Missing config file argument" << std::endl;
        printUsage(argv[0]);
        return 1;
    }
    
    config_file = argv[optind];
    
    try {
        std::string new_version = bumpVersion(config_file, bump_type);
        std::cout << new_version << std::endl; // Output for shell scripts
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
}