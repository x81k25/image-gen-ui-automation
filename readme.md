# AI Automation Suite - Dual-Mode Framework

A unified automation framework for both AI image generation and text completion services using Playwright browser automation.

## Overview

This project provides automated browser-based interactions with various AI services, supporting two distinct modes:

### Image Generation Services
- **DeepAI** - Text-to-image generation (Fully working)
- **Mock Service** - PIL-based image processing for testing (Always works)
- **Bing Image Creator** - Microsoft's image generation (Partial support)
- **Craiyon** - DALL-E mini implementation (Partial support)

### Text Completion Services
- **Google Gemini** - Advanced AI chat completion (Fully working)
- **OpenAI ChatGPT** - GPT-powered text generation (Partial support)
- **Anthropic Claude** - Claude AI assistant (Experimental)
- **Perplexity AI** - Search-powered AI responses (Experimental)

## Project Structure

```
.
├── main.py                          # Unified CLI interface
├── src/                             # Working automation scripts
│   ├── mock_image_alteration.py          # PIL-based image processing
│   ├── bing_image_alteration.py          # Bing Image Creator
│   ├── craiyon_image_alteration.py       # Craiyon (DALL-E mini)
│   ├── deepai_image_alteration.py        # DeepAI (confirmed working)
│   ├── openai_chat_completion.py         # ChatGPT text automation
│   ├── claude_chat_completion.py         # Claude text automation
│   ├── gemini_chat_completion.py         # Gemini text automation (working)
│   └── perplexity_chat_completion.py     # Perplexity text automation
├── test/                            # Experimental/non-working scripts
├── data/                            # Data directory
│   ├── input/                       # Input images
│   ├── output/                      # Generated content (images + text)
│   └── logs/                        # Session logs
└── requirements.txt                 # Python dependencies
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
python main.py --mode <mode> --service <service_name> [options]
```

### Available Options

- `--mode, -m`: Automation mode (default: image)
  - Options: `image`, `text`
- `--service, -s`: AI service to use (default: deepai for image, gemini for text)
- `--prompt, -p`: Text prompt for generation (default varies by mode)
- `--input, -i`: Input image file path (required for mock service only)
- `--output, -o`: Output directory (default: ./data/output/)
- `--list-services, -l`: List all available services and exit

### Examples

#### Image Generation Examples

##### Generate image with DeepAI (recommended - always works)
```bash
python main.py --mode image --service deepai --prompt "A futuristic city with flying cars"
```

##### Process existing image with mock service (always works)
```bash
python main.py --mode image --service mock --input ./data/input/dogs-playing-poker-original.jpg
```

##### Generate with Bing Image Creator
```bash
python main.py --mode image --service bing --prompt "A steampunk airship in the clouds"
```

##### Generate with Craiyon
```bash
python main.py --mode image --service craiyon --prompt "A dragon made of crystals"
```

#### Text Completion Examples

##### Chat with Gemini (recommended - verified working)
```bash
python main.py --mode text --service gemini --prompt "How do renewable energy sources work?"
```

##### Get response from ChatGPT
```bash
python main.py --mode text --service openai --prompt "Explain quantum computing in simple terms"
```

##### Ask Claude about programming
```bash
python main.py --mode text --service claude --prompt "What are the key principles of good software engineering?"
```

##### Query Perplexity for latest information
```bash
python main.py --mode text --service perplexity --prompt "What are the latest breakthroughs in artificial intelligence?"
```

#### Utility Commands

##### List all available services
```bash
python main.py --list-services
```

### Verified Working Examples

These examples are **guaranteed to work** based on our testing:

#### Image Generation - DeepAI
```bash
# Generate a cyberpunk scene (confirmed working)
python main.py --mode image --service deepai --prompt "A cyberpunk dragon breathing neon fire"
```
**Expected result:** 200x200 JPEG image saved to `./data/output/deepai-retry-2.jpg`

#### Image Processing - Mock Service
```bash
# Process an existing image (always works)
python main.py --mode image --service mock --input ./data/input/sample-original.jpg --prompt "Enhanced magical transformation"
```
**Expected result:** 1024x1024 JPEG with PIL transformations saved to `./data/output/mock-altered.jpg`

#### Text Completion - Gemini
```bash
# Get detailed explanation about renewable energy (confirmed working)
python main.py --mode text --service gemini --prompt "How do renewable energy sources work?"
```
**Expected result:** 3000+ character detailed response saved to `./data/output/gemini-text-completion.txt`

### Service-Specific Notes

#### Image Generation Services

##### DeepAI (Fully Working)
- No authentication required
- Generates 200x200 images
- Reliable and fast (~55 seconds)
- Real AI-generated content

##### Mock Service (Always Works)
- Requires input image
- Applies PIL transformations (color enhancement, contrast, sharpening)
- Instant processing (~0.12 seconds)
- Useful for testing pipeline

##### Bing Image Creator (Partial Support)
- Reaches interface successfully
- Submits prompts correctly
- Downloads SVG metadata instead of generated images
- May require authentication for full access

##### Craiyon (Partial Support)
- Reaches interface successfully
- Free tier has limitations
- Downloads logo SVGs instead of generated images
- Slower generation times (~70 seconds)

#### Text Completion Services

##### Google Gemini (Fully Working)
- No authentication required
- Generates comprehensive responses (3000+ characters)
- Reliable performance (~42 seconds)
- Produces detailed, well-structured answers

##### OpenAI ChatGPT (Partial Support)
- Reaches interface successfully
- Finds input fields and send buttons
- Response capture needs improvement
- May require login for full functionality

##### Anthropic Claude (Experimental)
- Interface detection challenges
- Input field location varies
- Requires further development

##### Perplexity AI (Experimental)
- Finds input fields successfully
- Submit button detection needs improvement
- Search-based approach requires refinement

## Output Files

### Image Generation
Generated images are saved with the following naming convention:
- Mock service: `mock-altered.jpg`
- AI services: `{service}-altered-{number}.jpg` or `{service}-retry-{number}.jpg`

### Text Completion
Generated text responses are saved as:
- Format: `{service}-text-completion.txt`
- Contains: Original prompt, service name, timestamp, and full response

### Session Logs
All automation runs are logged in `./data/logs/` with detailed execution information including:
- Start/end timestamps
- Execution time
- Success/failure status
- Output file paths
- Error details (if any)

## Troubleshooting

### Common Issues

1. **Module 'playwright' not found**
   - Ensure virtual environment is activated: `source .venv/bin/activate`
   - Reinstall playwright: `pip install playwright`

2. **Browser launch failed**
   - Install browser: `playwright install chromium`
   - Use virtual display on Linux: `xvfb-run -a python main.py ...`

3. **Service timeouts**
   - Some services have rate limits
   - Try again after a few minutes
   - Use DeepAI for images or Gemini for text for most reliable results

4. **No output files generated**
   - Check `./data/logs/` for detailed error information
   - Verify service status with `--list-services`
   - Use known working examples from this README

### Debug Mode

Check session logs in `./data/logs/` for detailed error information. Each automation run creates a timestamped JSON log with complete execution details.

## Development

### Adding New Services

#### For Image Generation:
1. Create new script: `src/{service}_image_alteration.py`
2. Add to `IMAGE_SERVICES` in `main.py`
3. Implement: `async def {service}_image_automation(output_dir: str, prompt: str) -> bool`

#### For Text Completion:
1. Create new script: `src/{service}_chat_completion.py`
2. Add to `CHAT_SERVICES` in `main.py`
3. Implement: `async def {service}_chat_automation(output_dir: str, prompt: str) -> bool`

### Testing

Use verified working services to test the pipeline:

```bash
# Test image generation pipeline
python main.py --mode image --service mock --input ./data/input/sample-original.jpg

# Test text completion pipeline
python main.py --mode text --service gemini --prompt "Test response"
```

## Success Statistics

Based on comprehensive testing:

- **Image Generation:** 2/4 services fully working (50% success rate)
  - WORKING: Mock, DeepAI
  - PARTIAL: Bing, Craiyon (interface access but limited output)

- **Text Completion:** 1/4 services fully working (25% success rate)
  - WORKING: Gemini
  - PARTIAL: OpenAI (interface access but response capture issues)
  - EXPERIMENTAL: Claude, Perplexity

- **Overall:** 3/8 services producing real outputs (37.5% full success rate)
- **Interface Access:** 5/8 services successfully reached (62.5% automation success)

## License

This project is for educational and research purposes only. Respect the terms of service of each AI platform.