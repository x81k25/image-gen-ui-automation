# AI Image Generation Automation Suite

A unified automation framework for multiple AI image generation services using Playwright browser automation.

## Overview

This project provides automated browser-based interactions with various AI image generation services, including:
- **DeepAI** - Text-to-image generation (✅ Fully working)
- **Mock Service** - PIL-based image processing for testing (✅ Always works)
- **Bing Image Creator** - Microsoft's image generation (⚠️ Partial support)
- **Craiyon** - DALL-E mini implementation (⚠️ Partial support)

## Project Structure

```
.
├── main.py                 # Unified CLI interface
├── src/                    # Working automation scripts
│   ├── mock_automation.py      # PIL-based image processing
│   ├── bing_automation.py      # Bing Image Creator
│   ├── craiyon_automation.py   # Craiyon (DALL-E mini)
│   └── deepai_retry.py         # DeepAI (confirmed working)
├── test/                   # Experimental/non-working scripts
├── data/                   # Data directory
│   ├── input/              # Input images
│   ├── output/             # Generated images
│   └── logs/               # Session logs
└── .dev/                   # Development/non-operational scripts
```

## Installation

1. Ensure you have Python 3.8+ installed
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

### Basic Command Structure

```bash
python main.py --service <service_name> [options]
```

### Available Options

- `--service, -s`: AI service to use (default: deepai)
  - Options: `mock`, `deepai`, `bing`, `craiyon`
- `--prompt, -p`: Text prompt for image generation (default: "A beautiful landscape with mountains and a lake at sunset")
- `--input, -i`: Input image file path (required for mock service)
- `--output, -o`: Output directory (default: ./data/output/)
- `--list-services, -l`: List all available services and exit

### Examples

#### Generate image with DeepAI (recommended)
```bash
python main.py --service deepai --prompt "A futuristic city with flying cars"
```

#### Process existing image with mock service
```bash
python main.py --service mock --input ./data/input/dogs-playing-poker-original.jpg
```

#### Generate with custom prompt and output directory
```bash
python main.py --service bing --prompt "Anthropomorphize these animals" --output ./results/
```

#### Generate with Craiyon
```bash
python main.py --service craiyon --prompt "A dragon made of crystals"
```

#### List all available services
```bash
python main.py --list-services
```

### Service-Specific Notes

#### DeepAI (✅ Fully Working)
- No authentication required
- Generates 512x512 images
- Reliable and fast
- Example: `python main.py --service deepai --prompt "A robot painting a sunset"`

#### Mock Service (✅ Always Works)
- Requires input image
- Applies PIL transformations
- Useful for testing pipeline
- Example: `python main.py --service mock --input ./data/input/sample-original.jpg`

#### Bing Image Creator (⚠️ Partial Support)
- May require authentication
- Downloads may be metadata only
- Example: `python main.py --service bing --prompt "Steampunk landscape"`

#### Craiyon (⚠️ Partial Support)
- Free tier has limitations
- Slower generation times
- Example: `python main.py --service craiyon --prompt "Pixel art castle"`

## Output Files

Generated images are saved with the following naming convention:
- Mock service: `{original_name}-altered.jpg`
- AI services: `{service}-altered-{number}.jpg`

Session logs are saved in `./data/logs/` with detailed execution information.

## Troubleshooting

### Common Issues

1. **Module 'playwright' not found**
   - Ensure virtual environment is activated: `source .venv/bin/activate`
   - Reinstall playwright: `pip install playwright`

2. **Browser launch failed**
   - Install browser: `playwright install chromium`
   - Check display (Linux): `echo $DISPLAY`

3. **Service timeouts**
   - Some services have rate limits
   - Try again after a few minutes
   - Use DeepAI for most reliable results

### Debug Mode

Check session logs in `./data/logs/` for detailed error information.

## Development

### Adding New Services

1. Create new automation script in `src/`
2. Add service definition to `AVAILABLE_SERVICES` in `main.py`
3. Implement async function with standard interface:
   ```python
   async def service_automation(output_dir: str, prompt: str) -> bool:
       # Implementation
       return success
   ```

### Testing

Use the mock service to test the pipeline without consuming API limits:
```bash
python main.py --service mock --input ./data/input/test-image.jpg
```

## License

This project is for educational and research purposes only. Respect the terms of service of each AI platform.