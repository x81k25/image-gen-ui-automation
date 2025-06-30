#!/usr/bin/env python3
"""
Google Gemini Chat Completion Automation
Automates browser interactions with Gemini to:
1. Navigate to https://gemini.google.com
2. Submit a text prompt
3. Capture and save the AI response
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def gemini_chat_automation(output_dir=None, prompt=None):
    """Main automation function for Google Gemini"""
    
    # Set up paths with defaults
    if output_dir is None:
        output_dir = Path("./data/output")
    else:
        output_dir = Path(output_dir)
    
    if prompt is None:
        prompt = "Explain the benefits and challenges of renewable energy sources"
    
    output_file = output_dir / "gemini-text-completion.txt"
    
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
            logging.info("Navigating to Google Gemini")
            await page.goto("https://gemini.google.com/", timeout=60000)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Look for chat interface
            logging.info("Looking for chat input")
            input_selectors = [
                'div[contenteditable="true"]',
                'textarea[placeholder*="Enter"]',
                'textarea[aria-label*="Message"]',
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
                
                # Look for send button
                send_selectors = [
                    'button[aria-label*="Send"]',
                    'button:has-text("Send")',
                    'button[type="submit"]',
                    '[data-testid="send-button"]',
                    'button[data-test-id="send-button"]'
                ]
                
                send_button = None
                for selector in send_selectors:
                    try:
                        send_button = await page.wait_for_selector(selector, timeout=5000)
                        if send_button:
                            logging.info(f"Found send button: {selector}")
                            break
                    except:
                        continue
                
                if send_button:
                    logging.info("Clicking send button")
                    await send_button.click()
                    
                    # Wait for response
                    logging.info("Waiting for Gemini response")
                    await asyncio.sleep(15)  # Gemini can take time
                    
                    # Look for response elements
                    response_selectors = [
                        '[data-response-index]',
                        '.model-response',
                        '[role="presentation"]',
                        '.markdown-content',
                        '.response-content'
                    ]
                    
                    for selector in response_selectors:
                        try:
                            await asyncio.sleep(3)  # Wait for response completion
                            
                            response_elements = await page.query_selector_all(selector)
                            if response_elements:
                                logging.info(f"Found {len(response_elements)} response elements")
                                
                                # Get the last response
                                for element in response_elements[-2:]:
                                    try:
                                        text_content = await element.text_content()
                                        if text_content and len(text_content.strip()) > 50:
                                            logging.info(f"Captured Gemini response ({len(text_content)} chars)")
                                            
                                            # Save response to file
                                            with open(output_file, 'w', encoding='utf-8') as f:
                                                f.write(f"Prompt: {prompt}\n\n")
                                                f.write(f"Response from Google Gemini:\n")
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
                    await page.screenshot(path="./debug/gemini_no_response.png")
                else:
                    logging.error("No send button found")
                    await page.screenshot(path="./debug/gemini_no_send.png")
            else:
                logging.error("Could not find input field")
                await page.screenshot(path="./debug/gemini_no_input.png")
                
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            await page.screenshot(path="./debug/gemini_error.png")
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
    success = asyncio.run(gemini_chat_automation())
    if success:
        logging.info("Gemini automation completed successfully")
    else:
        logging.error("Gemini automation failed")