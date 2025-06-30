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

# Available services and their modules
AVAILABLE_SERVICES = {
    "mock": {
        "module": "mock_automation",
        "function": "mock_image_automation",
        "description": "Mock automation using PIL transformations (always works)",
        "requires_input": True,
        "generates_new": True
    },
    "bing": {
        "module": "bing_automation", 
        "function": "bing_image_automation",
        "description": "Bing Image Creator automation",
        "requires_input": False,
        "generates_new": True
    },
    "craiyon": {
        "module": "craiyon_automation",
        "function": "craiyon_image_automation", 
        "description": "Craiyon (DALL-E mini) automation",
        "requires_input": False,
        "generates_new": True
    },
    "deepai": {
        "module": "deepai_automation",
        "function": "deepai_retry_automation",
        "description": "DeepAI Text-to-Image automation (confirmed working)",
        "requires_input": False,
        "generates_new": True
    }
}

DEFAULT_INPUT = "./data/input/dogs-playing-poker-original.jpg"
DEFAULT_OUTPUT_DIR = "./data/output/"
DEFAULT_PROMPT = "anthropomorphize these animals"
DEFAULT_SERVICE = "deepai"

class ImageGenerationRunner:
    """Main runner class for image generation automation"""
    
    def __init__(self, service: str, input_file: Optional[str] = None, 
                 output_dir: str = DEFAULT_OUTPUT_DIR, prompt: Optional[str] = None):
        self.service = service
        self.input_file = Path(input_file) if input_file else None
        self.output_dir = Path(output_dir)
        self.prompt = prompt or DEFAULT_PROMPT
        self.session_log = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_service(self) -> bool:
        """Validate that the requested service is available"""
        if self.service not in AVAILABLE_SERVICES:
            logging.error(f"Service '{self.service}' not available.")
            logging.info(f"Available services: {', '.join(AVAILABLE_SERVICES.keys())}")
            return False
        return True
    
    def validate_input(self) -> bool:
        """Validate input file if required"""
        service_info = AVAILABLE_SERVICES[self.service]
        
        if service_info["requires_input"]:
            if not self.input_file or not self.input_file.exists():
                logging.error(f"Service '{self.service}' requires input file: {self.input_file}")
                return False
            logging.info(f"Input file validated: {self.input_file}")
        else:
            logging.info(f"Service '{self.service}' generates images from prompt only")
        
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
        service_info = AVAILABLE_SERVICES[self.service]
        
        try:
            logging.info(f"Starting {self.service} automation")
            logging.info(f"Service: {service_info['description']}")
            
            if self.input_file:
                logging.info(f"Input: {self.input_file}")
            logging.info(f"Output: {self.output_dir}")
            logging.info(f"Prompt: {self.prompt}")
            
            self.log_session("automation_start", {
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
            
            if self.service == "mock":
                # Mock service needs input file and output dir
                success = await automation_function(
                    input_file=str(self.input_file) if self.input_file else None,
                    output_dir=str(self.output_dir)
                )
            else:
                # Other services need output dir and prompt
                success = await automation_function(
                    output_dir=str(self.output_dir),
                    prompt=self.prompt
                )
            
            execution_time = time.time() - start_time
            
            if success:
                logging.info(f"{self.service} automation completed successfully")
                logging.info(f"Execution time: {execution_time:.2f} seconds")
                
                self.log_session("automation_success", {
                    "execution_time": execution_time,
                    "output_files": self._find_output_files()
                })
                
                return True
            else:
                logging.error(f"{self.service} automation failed")
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
        for pattern in ["*.jpg", "*.png", "*.jpeg"]:
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
    logging.info("Available AI Image Generation Services:")
    logging.info("=" * 60)
    
    for service_id, info in AVAILABLE_SERVICES.items():
        status = "WORKING" if service_id in ["mock", "deepai"] else "PARTIAL"
        input_req = "Input Required" if info["requires_input"] else "Prompt Only"
        
        logging.info(f"{service_id.upper()}")
        logging.info(f"   Status: {status}")
        logging.info(f"   Type: {input_req}")
        logging.info(f"   Description: {info['description']}")
    
    logging.info("Example usage:")
    logging.info("   python main.py --service deepai --prompt 'A robot in space'")
    logging.info("   python main.py --service mock --input ./data/input/sample-original.jpg")

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
        "--service", "-s",
        default=DEFAULT_SERVICE,
        choices=list(AVAILABLE_SERVICES.keys()),
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
    runner = ImageGenerationRunner(
        service=args.service,
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
            logging.info("Image generation completed successfully")
            logging.info(f"Check output directory: {runner.output_dir}")
        else:
            logging.error("Image generation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logging.warning("Automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()