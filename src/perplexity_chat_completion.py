#!/usr/bin/env python3
"""
Perplexity AI Chat Completion Automation
Automates browser interactions with Perplexity to:
1. Navigate to https://perplexity.ai
2. Submit a text prompt
3. Capture and save the AI response
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def perplexity_chat_automation(output_dir=None, prompt=None):
    """Main automation function for Perplexity AI"""
    
    # Set up paths with defaults
    if output_dir is None:
        output_dir = Path("./data/output")
    else:
        output_dir = Path(output_dir)
    
    if prompt is None:
        prompt = "What are the latest developments in quantum computing?"
    
    output_file = output_dir / "perplexity-text-completion.txt"
    
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
                '--no-default-browser-check'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            logging.info("Navigating to Perplexity AI")
            await page.goto("https://www.perplexity.ai/", timeout=60000)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Look for chat interface
            logging.info("Looking for search/chat input")
            input_selectors = [
                'textarea[placeholder*="Ask"]',
                'textarea[placeholder*="Search"]',
                'div[contenteditable="true"]',
                'input[placeholder*="Ask"]',
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
                
                # Look for search/submit button
                submit_selectors = [
                    'button[aria-label*="Submit"]',
                    'button:has-text("Search")',
                    'button[type="submit"]',
                    '[data-testid="submit-button"]',
                    'button:has-text("Ask")'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = await page.wait_for_selector(selector, timeout=5000)
                        if submit_button:
                            logging.info(f"Found submit button: {selector}")
                            break
                    except:
                        continue
                
                if submit_button:
                    logging.info("Clicking submit button")
                    await submit_button.click()
                    
                    # Wait for response
                    logging.info("Waiting for Perplexity response")
                    await asyncio.sleep(15)  # Perplexity searches and generates
                    
                    # Look for response elements
                    response_selectors = [
                        '[data-testid*="answer"]',
                        '.prose',
                        '.answer-content',
                        '[role="main"]',
                        '.search-result'
                    ]
                    
                    for selector in response_selectors:
                        try:
                            await asyncio.sleep(3)  # Wait for response completion
                            
                            response_elements = await page.query_selector_all(selector)
                            if response_elements:
                                logging.info(f"Found {len(response_elements)} response elements")
                                
                                # Get the main response
                                for element in response_elements[:2]:  # Check first couple elements
                                    try:
                                        text_content = await element.text_content()
                                        if text_content and len(text_content.strip()) > 100:
                                            logging.info(f"Captured Perplexity response ({len(text_content)} chars)")
                                            
                                            # Save response to file
                                            with open(output_file, 'w', encoding='utf-8') as f:
                                                f.write(f"Prompt: {prompt}\n\n")
                                                f.write(f"Response from Perplexity AI:\n")
                                                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                                                f.write(text_content.strip())
                                            
                                            logging.info(f"Saved response to: {output_file}")
                                            return True
                                    except Exception as e:
                                        logging.error(f"Error extracting text: {e}")
                                        continue
                                break
                        except Exception as e:
                            logging.error(f"Error with selector {selector}: {e}")
                            continue
                    
                    logging.warning("No response found")
                    await page.screenshot(path="./debug/perplexity_no_response.png")
                else:
                    logging.error("No submit button found")
                    await page.screenshot(path="./debug/perplexity_no_submit.png")
            else:
                logging.error("Could not find input field")
                await page.screenshot(path="./debug/perplexity_no_input.png")
                
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            await page.screenshot(path="./debug/perplexity_error.png")
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
    success = asyncio.run(perplexity_chat_automation())
    if success:
        logging.info("Perplexity automation completed successfully")
    else:
        logging.error("Perplexity automation failed")