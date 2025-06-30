#!/usr/bin/env python3
"""
Bing Image Creator Automation
Automates browser interactions with Bing Image Creator to:
1. Navigate to Bing Image Creator
2. Enter a prompt to generate an image
3. Save the generated result
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def bing_image_automation(output_dir=None, prompt=None):
    """Main automation function for Bing Image Creator"""
    
    # Set up paths with defaults
    if output_dir is None:
        output_dir = Path("./data/output")
    else:
        output_dir = Path(output_dir)
    
    output_file = output_dir / "bing-altered.jpg"
    
    if prompt is None:
        prompt = "A majestic castle on a hill overlooking a valley with autumn colors, digital art"
    
    async with async_playwright() as p:
        # Launch browser with stealth settings
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-default-apps'
            ]
        )
        
        # Create context with realistic settings
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        page = await context.new_page()
        
        try:
            logging.info("Navigating to Bing Image Creator")
            await page.goto("https://www.bing.com/images/create", timeout=60000)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Look for the prompt input
            logging.info("Looking for prompt input")
            input_selectors = [
                'textarea[placeholder*="Describe"]',
                'input[placeholder*="prompt"]',
                'textarea[name="q"]',
                'input[name="q"]',
                'textarea',
                'input[type="text"]'
            ]
            
            input_field = None
            for selector in input_selectors:
                try:
                    input_field = await page.wait_for_selector(selector, timeout=10000)
                    if input_field:
                        logging.info(f"Found input field: {selector}")
                        break
                except:
                    continue
            
            if input_field:
                # Enter the prompt
                logging.info(f"Entering prompt: {prompt}")
                
                await input_field.click()
                await asyncio.sleep(1)
                await input_field.fill(prompt)
                await asyncio.sleep(2)
                
                # Look for create/generate button
                generate_selectors = [
                    'button:has-text("Create")',
                    'button:has-text("Generate")',
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Join & Create")',
                    '[data-testid="create-button"]'
                ]
                
                generate_button = None
                for selector in generate_selectors:
                    try:
                        generate_button = await page.wait_for_selector(selector, timeout=5000)
                        if generate_button:
                            logging.info(f"Found generate button: {selector}")
                            break
                    except:
                        continue
                
                if generate_button:
                    logging.info("Clicking generate button")
                    await generate_button.click()
                    
                    # Wait for generation to complete
                    logging.info("Waiting for image generation")
                    await asyncio.sleep(25)  # Bing can take time
                    
                    # Look for generated images
                    image_selectors = [
                        'img[src*="th?id=OIG"]',
                        'img[src*="bing.com"]',
                        'img[alt*="Generated"]',
                        '.img_cont img',
                        '.gi_container img',
                        'img[data-testid*="result"]'
                    ]
                    
                    generated_images = []
                    for selector in image_selectors:
                        try:
                            images = await page.query_selector_all(selector)
                            if images:
                                logging.info(f"Found {len(images)} images with selector: {selector}")
                                generated_images.extend(images)
                                break
                        except:
                            continue
                    
                    if generated_images:
                        # Try to download the first generated image
                        for i, img in enumerate(generated_images[:3]):  # Try first 3 images
                            try:
                                img_src = await img.get_attribute('src')
                                if img_src and 'bing.com' in img_src:
                                    logging.info(f"Attempting to download image {i+1}: {img_src}")
                                    
                                    # Download the image
                                    response = await context.request.get(img_src)
                                    if response.status == 200:
                                        image_data = await response.body()
                                        if len(image_data) > 1000:  # Ensure it's not a placeholder
                                            output_path = output_dir / f"bing-altered-{i+1}.jpg"
                                            with open(output_path, 'wb') as f:
                                                f.write(image_data)
                                            logging.info(f"Saved generated image to: {output_path}")
                                            return True
                                    else:
                                        logging.error(f"Failed to download image {i+1}: HTTP {response.status}")
                            except Exception as e:
                                logging.error(f"Error downloading image {i+1}: {e}")
                                continue
                        
                        logging.error("Could not download any generated images")
                    else:
                        logging.warning("No generated images found")
                        await page.screenshot(path="./debug/bing_no_result.png")
                else:
                    logging.error("No generate button found")
                    await page.screenshot(path="./debug/bing_no_button.png")
            else:
                logging.error("Could not find input field")
                await page.screenshot(path="./debug/bing_no_input.png")
                
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            await page.screenshot(path="./debug/bing_error.png")
            return False
        
        finally:
            await browser.close()
    
    return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    success = asyncio.run(bing_image_automation())
    if success:
        logging.info("Bing Image Creator automation completed successfully")
    else:
        logging.error("Bing Image Creator automation failed")