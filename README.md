# A Haven VLM Connector

A StashApp plugin for Vision-Language Model (VLM) based content tagging and analysis. This plugin leverages the Haven VLM Engine to provide advanced automatic content detection and tagging, delivering superior accuracy compared to traditional image classification methods.

## Features

- **Remote VLM Integration**: Connects to any OpenAI-compatible VLM endpoint (no local model loading required)
- **Context-Aware Detection**: Leverages Vision-Language Models' understanding of visual relationships for accurate content tagging
- **Flexible Architecture**: Modular pipeline system with configurable models and processing stages
- **Asynchronous Processing**: Built on asyncio for efficient video and image processing
- **Customizable Tag Sets**: Easy configuration of detection categories and confidence thresholds
- **Production Ready**: Includes retry logic, error handling, and comprehensive logging
- **Multiplexer Support**: Load balancing across multiple VLM endpoints with automatic failover
- **Advanced Dependency Management**: Uses PythonDepManager for automatic dependency installation and version management

## Requirements

- Python 3.8+
- StashApp
- PythonDepManager plugin (automatically handles all Python dependencies)
- Access to OpenAI-compatible VLM endpoints

## Installation

1. Clone or download this plugin to your StashApp plugins directory
2. Ensure PythonDepManager is installed in your StashApp plugins
3. Configure your VLM endpoints in `haven_vlm_config.py`
4. Restart StashApp

The plugin will automatically install and manage all required Python dependencies through PythonDepManager, including:
- `stashapp-tools>=0.2.58` (StashApp API integration)
- `aiohttp>=3.8.0` (Async HTTP client)
- `pydantic>=2.0.0` (Data validation)
- `vlm-engine>=1.0.0` (Haven VLM Engine)
- `pyyaml>=6.0.0` (YAML configuration)

## Dependency Management

This plugin uses PythonDepManager for advanced dependency management, providing:

- **Automatic Installation**: Dependencies are automatically installed when needed
- **Version Isolation**: Each plugin uses isolated dependency versions to prevent conflicts
- **Version Constraints**: Specific version requirements ensure compatibility
- **No Manual Setup**: Users don't need to manually install dependencies
- **Conflict Resolution**: Automatic handling of dependency conflicts between plugins

### How It Works

The plugin automatically ensures all dependencies are available before importing them:

```python
from PythonDepManager import ensure_import

# Install and ensure dependencies with version constraints
ensure_import(
    "stashapi:stashapp-tools>=0.2.58",
    "aiohttp>=3.8.0",
    "pydantic>=2.0.0",
    "vlm-engine>=1.0.0",
    "pyyaml>=6.0.0"
)

# Import dependencies after ensuring they're available
import stashapi.log as log
import aiohttp
import pydantic
# ... etc
```

## Configuration

The plugin uses a comprehensive configuration system in `haven_vlm_config.py`. Key configuration options:

### VLM Endpoints

Configure your VLM endpoints in the `multiplexer_endpoints` section:

```python
"multiplexer_endpoints": [
    {
        "base_url": "http://localhost:1234/v1",  # LM Studio default
        "api_key": "",
        "name": "lm-studio-primary",
        "weight": 5,
        "is_fallback": False
    },
    {
        "base_url": "https://vlm.sinbox.fun:443/v1",
        "api_key": "",
        "name": "cloud-fallback",
        "weight": 0,
        "is_fallback": True
    }
]
```

### Tag Configuration

Configure detection tags in the `tag_list` section:

```python
"tag_list": [
    "Kissing", "Hugging"
]
```

### Processing Settings

Adjust processing parameters:

```python
VIDEO_FRAME_INTERVAL = 2.0  # Process every 2 seconds
VIDEO_THRESHOLD = 0.3       # Confidence threshold for video detection
IMAGE_THRESHOLD = 0.5       # Confidence threshold for image detection
CONCURRENT_TASK_LIMIT = 10  # Number of concurrent processing tasks
```

## Usage

### Tag Videos

1. Tag scenes with the `VLM_TagMe` tag in StashApp
2. Run the "Tag Videos" task from the plugin interface
3. The plugin will process each video and add appropriate tags and markers

### Collect Incorrect Data

1. Manually tag incorrectly detected content with `VLM_Incorrect`
2. Run the "Collect Incorrect Markers and Images" task
3. Data will be exported to the `output_data` directory for analysis

### Find Optimal Settings

1. Tag exactly one scene with `VLM_TagMe`
2. Manually adjust markers to desired positions
3. Run the "Find Marker Settings" task
4. Review the optimal settings output

## Tag System

The plugin uses a hierarchical tag system:

- **VLM**: Base tag for all VLM-generated tags
- **VLM_TagMe**: Tag to mark content for processing
- **VLM_Tagged**: Tag applied to successfully processed content
- **VLM_Errored**: Tag applied to content that failed processing
- **VLM_Incorrect**: Tag for manually marking incorrect detections
- **VLM_UpdateMe**: Tag for content that needs reprocessing

## File Structure

```
AHavenVLMConnector/
├── ahavenvlmconnector.yml          # Plugin configuration (includes PythonDepManager requirement)
├── haven_vlm_connector.py          # Main plugin entry point with dependency management
├── haven_vlm_config.py             # Configuration management with dependency management
├── haven_vlm_engine.py             # VLM Engine integration with dependency management
├── haven_media_handler.py          # StashApp media operations with dependency management
├── haven_vlm_utility.py            # Utility functions with dependency management
├── requirements.txt                 # Development dependencies only
└── README.md                       # This file
```

## Troubleshooting

### Common Issues

1. **PythonDepManager not found**: Ensure PythonDepManager is installed in your StashApp plugins
2. **Dependency installation errors**: Check your internet connection and pip configuration
3. **Version conflicts**: PythonDepManager automatically handles version conflicts
4. **Connection errors**: Check your VLM endpoint URLs and network connectivity
5. **Permission errors**: Ensure StashApp has read/write access to media directories
6. **Memory issues**: Reduce `CONCURRENT_TASK_LIMIT` or `IMAGE_BATCH_SIZE`

### Dependency Management Issues

If you encounter dependency-related issues:

1. **Clear cached dependencies**:
   ```python
   from PythonDepManager import flush_dependencies
   flush_dependencies()
   ```

2. **Check dependency status**: Review the dependency installation logs in StashApp

3. **Manual dependency installation**: As a fallback, you can manually install dependencies:
   ```bash
   pip install stashapp-tools>=0.2.58 aiohttp>=3.8.0 pydantic>=2.0.0 vlm-engine>=1.0.0 pyyaml>=6.0.0
   ```

### Logging

Enable debug logging by modifying the logging level in the relevant modules:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

- Use multiple VLM endpoints for load balancing
- Adjust `CONCURRENT_TASK_LIMIT` based on your system capabilities
- Configure appropriate `VIDEO_FRAME_INTERVAL` for your use case
- Use SSD storage for better I/O performance

## Development

### Adding New Dependencies

To add new dependencies to the plugin:

1. Add the dependency to the `ensure_import` call in the relevant module
2. Specify version constraints for compatibility
3. Update the README documentation

Example:
```python
ensure_import("new-package>=1.0.0")
import new_package
```

### Adding New Tags

1. Add new tags to the `tag_list` in `haven_vlm_config.py`
2. Configure tag settings in the `category_config` section
3. Restart StashApp

### Custom VLM Endpoints

The plugin supports any OpenAI-compatible VLM endpoint. Ensure your endpoint:

- Accepts POST requests to `/v1/chat/completions`
- Returns responses in OpenAI format
- Supports vision models with image input

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the StashApp plugin documentation
3. Check the PythonDepManager documentation
4. Open an issue on the project repository
5. Check the Haven VLM Engine documentation

## Changelog

### Version 3.1.0
- **NEW**: Integrated PythonDepManager for advanced dependency management
- **IMPROVED**: Automatic dependency installation and version management
- **IMPROVED**: Isolated dependency versions to prevent conflicts
- **IMPROVED**: Better error handling for dependency-related issues
- **IMPROVED**: Simplified installation process for users

### Version 3.0.0
- Complete rewrite using Haven VLM Engine
- Improved naming conventions and architecture
- Enhanced configuration system
- Better error handling and logging