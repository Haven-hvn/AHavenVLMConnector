# Changelog

All notable changes to the A Haven VLM Connector project will be documented in this file.

## [Unreleased]

### Added
- **NEW VLM Engine Architectural Update** - Migrated from network-layer (httpx) to application-layer concurrency control
- **Intelligent Overflow Routing** - System now understands endpoint-specific capacity for better traffic distribution
- **Self-Healing & Rebalancing** - Load balancing is now stateless and per-request for optimal performance
- **Weighted Preservation Under Load** - Supports different concurrency limits per endpoint

### Changed
- **MIGRATION REQUIRED** - `connection_pool_size` parameter removed (deprecated)
- **NEW REQUIRED** - Added `max_concurrent` parameter to each multiplexer endpoint
- **Updated Global Settings** - `max_concurrent_requests` now 13 (10 primary + 2 fallback + 1 buffer)
- **Endpoint Configuration** - Primary server (lm-studio): max_concurrent=10, weight=95%
- **Endpoint Configuration** - Fallback server (cloud): max_concurrent=2, weight=5%

### Technical Details
- Application layer now manages traffic distribution instead of internet layer
- No more manual tuning of connection pools needed
- Automatic pool sizing based on `max_concurrent` values
- Immediate rebalancing when servers become available

### Breaking Changes
- **Connection Pool Configuration**: The `connection_pool_size` parameter is completely removed
- **Endpoint Requirements**: All multiplexer endpoints must now include `max_concurrent` field
- **Global Concurrency**: Carefully review and adjust `max_concurrent_requests` settings

## [1.0.0] - 2025-06-29

### Added
- **Initial release**
