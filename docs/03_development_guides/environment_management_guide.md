# Environment Management Guide

**Complete Environment Isolation System for Linch Mind**

**Version**: 1.0
**Implementation Date**: 2025-08-11
**Architecture**: V62 Environment Isolation
**Status**: ✅ Production Ready

---

## 🎯 Overview

Linch Mind now supports complete environment isolation with three distinct environments: development, staging, and production. Each environment provides complete data, configuration, and process isolation while maintaining full backward compatibility.

---

## 🏗️ Environment Architecture

### Supported Environments

1. **Development** (`development`)
   - **Purpose**: Local development and debugging
   - **Database**: Unencrypted SQLite for fast iteration
   - **Debug Mode**: Enabled with detailed logging
   - **Performance**: Monitoring enabled for optimization
   - **Backup**: Disabled for faster development

2. **Staging** (`staging`)
   - **Purpose**: Pre-production testing and validation
   - **Database**: SQLCipher encrypted for security testing
   - **Debug Mode**: Enabled with performance monitoring
   - **Performance**: Full monitoring and metrics
   - **Backup**: Automatic backup enabled

3. **Production** (`production`)
   - **Purpose**: Live production deployment
   - **Database**: SQLCipher encrypted with optimized settings
   - **Debug Mode**: Disabled for security and performance
   - **Performance**: Optimized connection pools and caching
   - **Backup**: Automatic backup with retention policies

---

## 📁 Directory Structure

Each environment maintains complete isolation with dedicated directories:

```
~/.linch-mind/
├── development/
│   ├── config/          # Environment-specific configurations
│   ├── data/            # Application data and user content
│   ├── logs/            # Log files and debug information
│   ├── cache/           # Temporary cache and working files
│   ├── vectors/         # FAISS vector indexes and AI models
│   └── database/        # SQLite database files
├── staging/
│   └── (same structure)
├── production/
│   └── (same structure)
└── shared/
    └── models/          # Shared AI models across environments
```

---

## 🚀 Quick Start Guide

### Environment Initialization

**First-time setup or new environment:**

```bash
# Initialize development environment (default)
./linch-mind init

# Initialize specific environment
./linch-mind init production
./linch-mind init staging --force    # Force reinitialize

# Initialize with options
./linch-mind init staging --skip-models --verbose
```

### Environment Detection

The system automatically detects the current environment using:

1. **Environment Variable** (Primary): `LINCH_ENV`
2. **Test Detection**: `PYTEST_CURRENT_TEST`, `TESTING=1`
3. **Production Detection**: `PRODUCTION=1`, `NODE_ENV=production`
4. **Default**: `development`

```bash
# Set environment explicitly
export LINCH_ENV=production
./linch-mind start

# Temporary environment for single command
LINCH_ENV=staging ./linch-mind status
```

---

## 🔧 Usage Examples

### Basic Environment Commands

```bash
# System health check
./linch-mind doctor

# View current environment status
./linch-mind status

# Reset environment data (with confirmation)
./linch-mind reset staging
./linch-mind reset development --yes    # Skip confirmation
```

### Programmatic Environment Access

```python
from core.service_facade import get_environment_manager
from core.environment_manager import Environment

# Get environment manager
env_manager = get_environment_manager()

# Check current environment
print(f"Current environment: {env_manager.current_environment.value}")
print(f"Database URL: {env_manager.get_database_url()}")
print(f"Data directory: {env_manager.get_data_dir()}")

# Get environment-specific paths
paths = env_manager.get_environment_paths()
print(f"Config path: {paths['config']}")
print(f"Logs path: {paths['logs']}")
```

### Environment Switching

```python
# Temporary environment switch (context manager)
with env_manager.switch_environment(Environment.PRODUCTION):
    # All operations run in production environment
    database_service = get_service(DatabaseService)
    # Database operations use production database
    pass
# Automatically switches back to original environment

# Check if permanent switch is needed (requires restart)
if env_manager.requires_restart_for_switch(Environment.STAGING):
    print("Permanent switch requires daemon restart")
    env_manager.permanently_switch_environment(Environment.STAGING)
```

---

## ⚙️ Configuration Management

### Environment-Specific Configuration

The system uses intelligent configuration inheritance:

```
Final Configuration = Default Config + Environment Config + Database Config
```

**Priority Order**: Database Config > Environment Config > Default Config

### Configuration Templates

Environment templates are located in `/daemon/config/templates/`:

- `development.yaml` - Development environment settings
- `staging.yaml` - Staging environment settings
- `production.yaml` - Production environment settings

### Example Environment Configuration

```yaml
# ~/.linch-mind/development/config/environment.yaml
database:
  encryption_enabled: false
  debug_logging: true
  connection_pool_size: 5

performance:
  cache_enabled: true
  monitoring_enabled: true
  profiling_enabled: true

security:
  strict_mode: false
  audit_logging: false

backup:
  enabled: false
  retention_days: 7
```

---

## 🔒 Security and Production Features

### Development Environment
- **Database**: Unencrypted SQLite for fast development
- **Debugging**: Full debug logging and profiling enabled
- **Security**: Relaxed security for ease of development
- **Backup**: Disabled to avoid unnecessary overhead

### Staging Environment
- **Database**: SQLCipher encryption enabled
- **Debugging**: Debug mode with performance monitoring
- **Security**: Production-level security with audit logging
- **Backup**: Automatic backup with 30-day retention

### Production Environment
- **Database**: SQLCipher encryption with optimized settings
- **Debugging**: Debug mode disabled, error logging only
- **Security**: Full security mode with comprehensive auditing
- **Backup**: Automatic backup with configurable retention

---

## 🔍 Advanced Features

### Environment Information API

IPC endpoints for environment management:

- `GET /environment/current` - Current environment details
- `GET /environment/list` - Available environments
- `POST /environment/switch` - Switch environment (temporary)
- `GET /environment/paths` - Environment-specific paths
- `POST /environment/initialize` - Initialize environment
- `DELETE /environment/cleanup` - Cleanup environment data

### Database Isolation

Each environment maintains completely separate databases:

```python
# Environment-specific database URLs
development: sqlite:///~/.linch-mind/development/database/linch_mind_dev.db
staging:     sqlite:///~/.linch-mind/staging/database/linch_mind_staging.db
production:  sqlite:///~/.linch-mind/production/database/linch_mind.db
```

### Configuration Merging

Smart configuration merging with environment awareness:

```python
from core.environment_manager import get_environment_manager

env_manager = get_environment_manager()

# Load configuration with environment-specific overrides
config = env_manager.load_environment_config()

# Environment-specific database settings
db_config = env_manager.get_database_config()
```

---

## 🛡️ Best Practices

### Development Workflow

1. **Local Development**:
   ```bash
   export LINCH_ENV=development
   ./linch-mind init
   ./linch-mind start
   ```

2. **Testing Changes**:
   ```bash
   ./linch-mind init staging --force
   LINCH_ENV=staging ./linch-mind start
   ```

3. **Production Deployment**:
   ```bash
   export LINCH_ENV=production
   ./linch-mind init production
   ./linch-mind start
   ```

### Environment Hygiene

- **Never mix environments**: Each environment should maintain complete isolation
- **Use appropriate encryption**: Always use SQLCipher in staging/production
- **Monitor resource usage**: Different environments have different resource profiles
- **Regular cleanup**: Use `./linch-mind reset` to clean development environments

### Security Considerations

- **Environment Variables**: Never commit `.env` files with production credentials
- **Database Files**: Ensure production database files have proper permissions
- **Backup Security**: Production backups should be encrypted and secured
- **Access Control**: Limit access to production environment directories

---

## 🔧 Troubleshooting

### Common Issues

**Environment Not Detected**:
```bash
# Check environment variable
echo $LINCH_ENV

# Force environment detection
./linch-mind doctor --verbose
```

**Database Connection Issues**:
```bash
# Check database permissions and encryption
ls -la ~/.linch-mind/*/database/

# Reinitialize database
./linch-mind reset [env] --yes
./linch-mind init [env]
```

**Configuration Problems**:
```bash
# Validate environment configuration
./linch-mind doctor --check-config

# Reset configuration to defaults
rm ~/.linch-mind/*/config/environment.yaml
./linch-mind init [env] --force
```

### Debug Mode

Enable detailed environment debugging:

```bash
export LINCH_ENV_DEBUG=1
./linch-mind doctor --verbose
```

---

## 📈 Monitoring and Maintenance

### Health Checks

The `./linch-mind doctor` command provides comprehensive health checks:

- Environment detection and configuration
- Directory structure validation
- Database connectivity and encryption status
- Service registration and availability
- Performance metrics and resource usage

### Maintenance Tasks

**Regular Maintenance**:
```bash
# Weekly health check
./linch-mind doctor

# Clean up development environment monthly
./linch-mind reset development --yes
./linch-mind init development

# Backup production data (automatic in production environment)
# Verify staging environment monthly
LINCH_ENV=staging ./linch-mind doctor
```

---

## 🔗 Integration

### ServiceFacade Integration

Environment manager is fully integrated with the ServiceFacade pattern:

```python
from core.service_facade import get_environment_manager

# Get environment manager through ServiceFacade
env_manager = get_environment_manager()

# All environment operations available
current_env = env_manager.current_environment
database_url = env_manager.get_database_url()
```

### IPC Integration

Complete IPC API support for environment management:

```python
# IPC client example
ipc_client.send_request("GET", "/environment/current")
ipc_client.send_request("POST", "/environment/switch", {"environment": "staging"})
```

---

## 🎉 Benefits

### For Developers
- **Clean Development**: Isolated development environment with debug features
- **Easy Testing**: Seamless environment switching for testing
- **Fast Iteration**: Unencrypted development database for speed

### For Operations
- **Production Safety**: Complete isolation prevents data contamination
- **Staged Deployment**: Proper staging environment for testing
- **Easy Maintenance**: Simple environment cleanup and reset

### For System Architecture
- **Scalability**: Environment-specific optimization and resource allocation
- **Security**: Proper encryption and security policies per environment
- **Maintainability**: Clear separation of concerns and configuration management

---

**Environment System Status**: ✅ Production Ready
**Implementation**: Complete with full test coverage
**Backward Compatibility**: 100% - No breaking changes
**Next Steps**: UI environment management interface integration
