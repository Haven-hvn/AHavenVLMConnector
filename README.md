# A Haven VLM Connector

A StashApp plugin for Vision-Language Model (VLM) based content tagging and analysis. This plugin is designed with a **local-first philosophy**, empowering users to run analysis on their own hardware (using CPU or GPU) and their local network. It also supports cloud-based VLM endpoints for additional flexibility. The Haven VLM Engine provides advanced automatic content detection and tagging, delivering superior accuracy compared to traditional image classification methods.

## Features

- **Flexible Deployment**: Run on your local hardware (CPU or GPU) or balance load across multiple machines on your local network
- **Local Network Empowerment**: Distribute processing across home/office computers without cloud dependencies
- **Context-Aware Detection**: Leverages Vision-Language Models' understanding of visual relationships
- **Modular Architecture**: Configurable pipeline with customizable processing stages
- **Asynchronous Processing**: Built on asyncio for efficient video and image handling
- **Production Ready**: Robust retry logic, error handling, and comprehensive logging
- **Multiplexer Support**: Intelligent load balancing across multiple endpoints with automatic failover
- **Advanced Dependency Management**: Uses PythonDepManager for automatic dependency installation

## Requirements

- Python 3.8+
- StashApp
- PythonDepManager plugin (automatically handles dependencies)
- OpenAI-compatible VLM endpoints (local or cloud-based)

## Installation

1. Clone or download this plugin to your StashApp plugins directory
2. Ensure PythonDepManager is installed in your StashApp plugins
3. Configure your VLM endpoints in `haven_vlm_config.py` (local network endpoints recommended)
4. Restart StashApp

The plugin automatically manages all dependencies:
- `stashapp-tools>=0.2.58` (StashApp API)
- `aiohttp>=3.12.13` (Async HTTP)
- `pydantic>=2.0.0` (Data validation)
- `vlm-engine>=1.0.0` (Haven VLM Engine)
- `pyyaml>=6.0.0` (YAML configuration)

## Why Local-First?

- **Complete Control**: Process sensitive content on your own hardware
- **Cost Effective**: Avoid cloud processing fees by using existing resources
- **Flexible Scaling**: Add more computers to your local network for increased capacity
- **Privacy Focused**: Keep your media completely private
- **Hybrid Options**: Combine local and cloud endpoints for optimal flexibility

```mermaid
graph LR
A[User's Computer] --> B[Local GPU Machine]
A --> C[Local CPU Machine 1]
A --> D[Local CPU Machine 2]
A --> E[Cloud Endpoint]
```

## Configuration

### Easy Setup with LM Studio

[LM Studio](https://lmstudio.ai/) provides the easiest way to configure local endpoints:

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Search for or download a vision-capable model like Haven VLM - https://havenmodels.orbiter.website/
3. Load your desired Model
4. On the developer tab start the local server using the start toggle
5. Optionally click the Settings gear then toggle *Serve on local network*
5. Optionally configure `haven_vlm_config.py`:

By default locahost is included in the config, **remove cloud endpoint if you don't want automatic failover**
```python
{
    "base_url": "http://localhost:1234/v1",  # LM Studio default
    "api_key": "",                          # API key not required
    "name": "lm-studio-local",
    "weight": 5,
    "is_fallback": False
}
```

### Tag Configuration

```python
"tag_list": [
    "Basketball point", "Foul", "Break-away", "Turnover"
]
```

### Processing Settings

```python
VIDEO_FRAME_INTERVAL = 2.0  # Process every 2 seconds
CONCURRENT_TASK_LIMIT = 8   # Adjust based on local hardware
```

## Usage

### Tag Videos
1. Tag scenes with `VLM_TagMe`
2. Run "Tag Videos" task
3. Plugin processes content using local/network resources

### Performance Tips
- Start with 2-3 local machines for load balancing
- Assign higher weights to GPU-enabled machines
- Adjust `CONCURRENT_TASK_LIMIT` based on total system resources
- Use SSD storage for better I/O performance

## File Structure

```
AHavenVLMConnector/
├── ahavenvlmconnector.yml
├── haven_vlm_connector.py
├── haven_vlm_config.py
├── haven_vlm_engine.py
├── haven_media_handler.py
├── haven_vlm_utility.py
├── requirements.txt
└── README.md
```

## Troubleshooting

### Local Network Setup
- Ensure firewalls allow communication between machines
- Verify all local endpoints are running VLM services
- Use static IPs for local machines
- Check `http://local-machine-ip:port/v1` responds correctly

### Performance Optimization
- **Distribute Load**: Use multiple mid-range machines instead of one high-end
- **GPU Prioritization**: Assign highest weight to GPU machines
- **Network Speed**: Use wired Ethernet connections for faster transfer
- **Resource Monitoring**: Watch system resources during processing

## Development

### Adding Local Endpoints
1. Install VLM service on network machines
2. Add endpoint configuration with local IPs
3. Set appropriate weights based on hardware capability

### Custom Models
Use any OpenAI-compatible models that support:
- POST requests to `/v1/chat/completions`
- Vision capabilities with image input
- Local deployment options

## License
MIT License - see LICENSE for details

## Changelog
