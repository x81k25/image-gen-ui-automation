#!/usr/bin/env python3
"""
AI Image Generation Automation - Main Interface
Unified interface for all image generation services

Usage:
    python main.py --service deepai --input ./data/input/sample-original.jpg --output ./data/output/
    python main.py --service mock --prompt "A beautiful sunset"
    python main.py --list-services
"""

import argparse
import asyncio
import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Available image generation services and their modules
IMAGE_SERVICES = {
    "mock": {
        "module": "mock_image_alteration",
        "function": "mock_image_automation",
        "description": "Mock automation using PIL transformations (always works)",
        "requires_input": True,
        "generates_new": True
    },
    "bing": {
        "module": "bing_image_alteration", 
        "function": "bing_image_automation",
        "description": "Bing Image Creator automation",
        "requires_input": False,
        "generates_new": True
    },
    "craiyon": {
        "module": "craiyon_image_alteration",
        "function": "craiyon_image_automation", 
        "description": "Craiyon (DALL-E mini) automation",
        "requires_input": False,
        "generates_new": True
    },
    "deepai": {
        "module": "deepai_image_alteration",
        "function": "deepai_retry_automation",
        "description": "DeepAI Text-to-Image automation (confirmed working)",
        "requires_input": False,
        "generates_new": True
    }
}

# Available chat completion services and their modules
CHAT_SERVICES = {
    "openai": {
        "module": "openai_chat_completion",
        "function": "openai_chat_automation",
        "description": "OpenAI ChatGPT web interface automation",
        "requires_input": False,
        "generates_text": True
    },
    "claude": {
        "module": "claude_chat_completion",
        "function": "claude_chat_automation",
        "description": "Anthropic Claude web interface automation",
        "requires_input": False,
        "generates_text": True
    },
    "gemini": {
        "module": "gemini_chat_completion",
        "function": "gemini_chat_automation",
        "description": "Google Gemini web interface automation",
        "requires_input": False,
        "generates_text": True
    },
    "perplexity": {
        "module": "perplexity_chat_completion",
        "function": "perplexity_chat_automation",
        "description": "Perplexity AI web interface automation",
        "requires_input": False,
        "generates_text": True
    }
}

DEFAULT_INPUT = "./data/input/dogs-playing-poker-original.jpg"
DEFAULT_OUTPUT_DIR = "./data/output/"
DEFAULT_PROMPT = "anthropomorphize these animals"
DEFAULT_SERVICE = "deepai"
DEFAULT_MODE = "image"

class AutomationRunner:
    """Main runner class for both image generation and text completion automation"""
    
    def __init__(self, service: str, mode: str = DEFAULT_MODE, input_file: Optional[str] = None, 
                 output_dir: str = DEFAULT_OUTPUT_DIR, prompt: Optional[str] = None):
        self.service = service
        self.mode = mode
        self.input_file = Path(input_file) if input_file else None
        self.output_dir = Path(output_dir)
        self.prompt = prompt or DEFAULT_PROMPT
        self.session_log = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_service(self) -> bool:
        """Validate that the requested service is available"""
        available_services = IMAGE_SERVICES if self.mode == "image" else CHAT_SERVICES
        
        if self.service not in available_services:
            logging.error(f"Service '{self.service}' not available for {self.mode} mode.")
            logging.info(f"Available {self.mode} services: {', '.join(available_services.keys())}")
            return False
        return True
    
    def validate_input(self) -> bool:
        """Validate input file if required"""
        available_services = IMAGE_SERVICES if self.mode == "image" else CHAT_SERVICES
        service_info = available_services[self.service]
        
        if self.mode == "image" and service_info.get("requires_input", False):
            if not self.input_file or not self.input_file.exists():
                logging.error(f"Service '{self.service}' requires input file: {self.input_file}")
                return False
            logging.info(f"Input file validated: {self.input_file}")
        else:
            mode_type = "images" if self.mode == "image" else "text responses"
            logging.info(f"Service '{self.service}' generates {mode_type} from prompt only")
        
        return True
    
    def log_session(self, event: str, details: Dict[str, Any]):
        """Log session events"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "service": self.service,
            "event": event,
            "details": details
        }
        self.session_log.append(log_entry)
    
    async def run_service(self) -> bool:
        """Run the selected service automation"""
        available_services = IMAGE_SERVICES if self.mode == "image" else CHAT_SERVICES
        service_info = available_services[self.service]
        
        try:
            logging.info(f"Starting {self.service} {self.mode} automation")
            logging.info(f"Service: {service_info['description']}")
            
            if self.input_file:
                logging.info(f"Input: {self.input_file}")
            logging.info(f"Output: {self.output_dir}")
            logging.info(f"Prompt: {self.prompt}")
            
            self.log_session("automation_start", {
                "mode": self.mode,
                "input_file": str(self.input_file) if self.input_file else None,
                "output_dir": str(self.output_dir),
                "prompt": self.prompt
            })
            
            # Import and run the service module
            module_name = service_info["module"]
            function_name = service_info["function"]
            
            # Dynamic import
            module = __import__(module_name, fromlist=[function_name])
            automation_function = getattr(module, function_name)
            
            # Execute the automation
            start_time = time.time()
            
            if self.mode == "image" and self.service == "mock":
                # Mock service needs input file and output dir
                success = await automation_function(
                    input_file=str(self.input_file) if self.input_file else None,
                    output_dir=str(self.output_dir)
                )
            else:
                # All other services need output dir and prompt
                success = await automation_function(
                    output_dir=str(self.output_dir),
                    prompt=self.prompt
                )
            
            execution_time = time.time() - start_time
            
            if success:
                logging.info(f"{self.service} {self.mode} automation completed successfully")
                logging.info(f"Execution time: {execution_time:.2f} seconds")
                
                self.log_session("automation_success", {
                    "execution_time": execution_time,
                    "output_files": self._find_output_files()
                })
                
                return True
            else:
                logging.error(f"{self.service} {self.mode} automation failed")
                self.log_session("automation_failed", {
                    "execution_time": execution_time
                })
                return False
                
        except Exception as e:
            logging.error(f"Error running {self.service}: {e}")
            self.log_session("automation_error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    def _find_output_files(self) -> list:
        """Find output files in the output directory"""
        output_files = []
        if self.mode == "image":
            for pattern in ["*.jpg", "*.png", "*.jpeg"]:
                output_files.extend(list(self.output_dir.glob(pattern)))
        else:  # text mode
            for pattern in ["*.txt"]:
                output_files.extend(list(self.output_dir.glob(pattern)))
        return [str(f) for f in output_files]
    
    def save_session_log(self):
        """Save session log to file"""
        log_dir = Path("./data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"session_log_{self.service}_{int(time.time())}.json"
        with open(log_file, 'w') as f:
            json.dump(self.session_log, f, indent=2)
        logging.info(f"Session log saved: {log_file}")

def list_services():
    """List all available services"""
    logging.info("Available AI Automation Services:")
    logging.info("=" * 60)
    
    logging.info("\nIMAGE GENERATION SERVICES:")
    for service_id, info in IMAGE_SERVICES.items():
        status = "WORKING" if service_id in ["mock", "deepai"] else "PARTIAL"
        input_req = "Input Required" if info.get("requires_input", False) else "Prompt Only"
        
        logging.info(f"  {service_id.upper()}")
        logging.info(f"     Status: {status}")
        logging.info(f"     Type: {input_req}")
        logging.info(f"     Description: {info['description']}")
    
    logging.info("\nTEXT COMPLETION SERVICES:")
    for service_id, info in CHAT_SERVICES.items():
        logging.info(f"  {service_id.upper()}")
        logging.info(f"     Status: EXPERIMENTAL")
        logging.info(f"     Type: Prompt Only")
        logging.info(f"     Description: {info['description']}")
    
    logging.info("\nExample usage:")
    logging.info("   # Image generation")
    logging.info("   python main.py --mode image --service deepai --prompt 'A robot in space'")
    logging.info("   python main.py --mode image --service mock --input ./data/input/sample.jpg")
    logging.info("   # Text completion")
    logging.info("   python main.py --mode text --service openai --prompt 'Explain AI'")
    logging.info("   python main.py --mode text --service claude --prompt 'What is machine learning?'")

def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    parser = argparse.ArgumentParser(
        description="AI Image Generation Automation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --service deepai --prompt "A castle in the clouds"
  python main.py --service mock --input ./data/input/sample-original.jpg
  python main.py --service bing --output ./results/
  python main.py --list-services
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        default=DEFAULT_MODE,
        choices=["image", "text"],
        help=f"Automation mode: image generation or text completion (default: {DEFAULT_MODE})"
    )
    
    parser.add_argument(
        "--service", "-s",
        default=DEFAULT_SERVICE,
        help=f"AI service to use (default: {DEFAULT_SERVICE})"
    )
    
    parser.add_argument(
        "--input", "-i",
        default=DEFAULT_INPUT,
        help=f"Input image file path (default: {DEFAULT_INPUT})"
    )
    
    parser.add_argument(
        "--output", "-o", 
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        default=DEFAULT_PROMPT,
        help=f"Text prompt for image generation (default: '{DEFAULT_PROMPT}')"
    )
    
    parser.add_argument(
        "--list-services", "-l",
        action="store_true",
        help="List all available services and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_services:
        list_services()
        return
    
    # Create and run automation
    runner = AutomationRunner(
        service=args.service,
        mode=args.mode,
        input_file=args.input if args.input != DEFAULT_INPUT or Path(args.input).exists() else None,
        output_dir=args.output,
        prompt=args.prompt
    )
    
    # Validate inputs
    if not runner.validate_service() or not runner.validate_input():
        sys.exit(1)
    
    # Run automation
    try:
        success = asyncio.run(runner.run_service())
        runner.save_session_log()
        
        if success:
            completion_type = "Image generation" if runner.mode == "image" else "Text completion"
            logging.info(f"{completion_type} completed successfully")
            logging.info(f"Check output directory: {runner.output_dir}")
        else:
            completion_type = "Image generation" if runner.mode == "image" else "Text completion"
            logging.error(f"{completion_type} failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logging.warning("Automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()