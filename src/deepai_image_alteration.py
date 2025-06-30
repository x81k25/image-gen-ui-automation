#!/usr/bin/env python3
"""
DeepAI Text to Image 
Simplified automation focusing on core functionality
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def deepai_retry_automation(output_dir=None, prompt=None):
    """Retry DeepAI with improved selectors"""
    
    if output_dir is None:
        data_dir = Path("./data/output")
    else:
        data_dir = Path(output_dir)
    
    if prompt is None:
        prompt = "A robot painting a masterpiece in an art studio"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            deepai_urls = [
                "https://deepai.org/machine-learning-model/text2img",
                "https://deepai.org/machine-learning-model/cute-creature-generator",
                "https://deepai.org/"
            ]
            
            for url in deepai_urls:
                try:
                    logging.info(f"Trying DeepAI: {url}")
                    await page.goto(url, timeout=30000)
                    await asyncio.sleep(6)
                    
                    # Look for text input area
                    input_selectors = [
                        'textarea[name="text"]',
                        'textarea[placeholder*="Enter"]',
                        'input[name="text"]',
                        'textarea',
                        'input[type="text"]',
                        '#text-input'
                    ]
                    
                    input_field = None
                    for selector in input_selectors:
                        try:
                            input_field = await page.wait_for_selector(selector, timeout=8000)
                            if input_field:
                                logging.info(f"Found input: {selector}")
                                break
                        except:
                            continue
                    
                    if input_field:
                        logging.info(f"Entering: {prompt}")
                        
                        await input_field.click()
                        await asyncio.sleep(1)
                        await input_field.fill(prompt)
                        await asyncio.sleep(2)
                        
                        # Look for generate/submit button
                        submit_selectors = [
                            'input[value*="Generate"]',
                            'button:has-text("Generate")',
                            'input[type="submit"]',
                            'button[type="submit"]',
                            '#generate-button',
                            'button:has-text("Submit")'
                        ]
                        
                        for selector in submit_selectors:
                            try:
                                submit_btn = await page.wait_for_selector(selector, timeout=5000)
                                if submit_btn:
                                    logging.info(f"Found submit: {selector}")
                                    await submit_btn.click()
                                    logging.info("Waiting for generation")
                                    await asyncio.sleep(20)
                                    
                                    # Look for result images
                                    result_selectors = [
                                        'img[src*="deepai"]',
                                        'img[id*="output"]',
                                        '#output img',
                                        '.result-image img',
                                        'img[alt*="Generated"]'
                                    ]
                                    
                                    for img_sel in result_selectors:
                                        try:
                                            images = await page.query_selector_all(img_sel)
                                            if images:
                                                logging.info(f"Found {len(images)} images")
                                                
                                                for i, img in enumerate(images[:2]):
                                                    img_src = await img.get_attribute('src')
                                                    if img_src:
                                                        logging.info(f"Image {i+1}: {img_src[:100]}")
                                                        
                                                        if img_src.startswith('data:image'):
                                                            # Handle data URL
                                                            import base64
                                                            header, data = img_src.split(',', 1)
                                                            image_data = base64.b64decode(data)
                                                            if len(image_data) > 5000:
                                                                output_path = data_dir / f"deepai-retry-{i+1}.png"
                                                                with open(output_path, 'wb') as f:
                                                                    f.write(image_data)
                                                                logging.info(f"SUCCESS! Saved: {output_path}")
                                                                return True
                                                        else:
                                                            # Handle regular URL
                                                            if img_src.startswith('/'):
                                                                img_src = f"https://deepai.org{img_src}"
                                                            elif not img_src.startswith('http'):
                                                                img_src = f"https://deepai.org/{img_src}"
                                                            
                                                            response = await context.request.get(img_src)
                                                            if response.status == 200:
                                                                image_data = await response.body()
                                                                if len(image_data) > 5000:
                                                                    output_path = data_dir / f"deepai-retry-{i+1}.jpg"
                                                                    with open(output_path, 'wb') as f:
                                                                        f.write(image_data)
                                                                    logging.info(f"SUCCESS! Saved: {output_path}")
                                                                    return True
                                                break
                                        except:
                                            continue
                                    break
                            except:
                                continue
                        
                        # Found interface, break URL loop
                        break
                        
                except Exception as e:
                    logging.error(f"Error with {url}: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"General error: {e}")
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
    success = asyncio.run(deepai_retry_automation())
    if success:
        logging.info("DeepAI retry completed successfully")
    else:
        logging.error("DeepAI retry failed")