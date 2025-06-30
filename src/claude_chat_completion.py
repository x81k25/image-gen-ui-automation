#!/usr/bin/env python3
"""
Anthropic Claude Chat Completion Automation
Automates browser interactions with Claude to:
1. Navigate to https://claude.ai
2. Submit a text prompt
3. Capture and save the AI response
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def claude_chat_automation(output_dir=None, prompt=None):
    """Main automation function for Anthropic Claude"""
    
    # Set up paths with defaults
    if output_dir is None:
        output_dir = Path("./data/output")
    else:
        output_dir = Path(output_dir)
    
    if prompt is None:
        prompt = "What are the key principles of good software engineering?"
    
    output_file = output_dir / "claude-text-completion.txt"
    
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
            logging.info("Navigating to Claude AI")
            await page.goto("https://claude.ai/", timeout=60000)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Look for chat interface
            logging.info("Looking for chat input")
            input_selectors = [
                'div[contenteditable="true"]',
                'textarea[placeholder*="Talk"]',
                'textarea[placeholder*="Message"]',
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
                    'svg[data-icon="send"]',
                    '[data-testid="send-button"]'
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
                    logging.info("Waiting for Claude response")
                    await asyncio.sleep(12)  # Claude can take time to respond
                    
                    # Look for response elements
                    response_selectors = [
                        '[data-testid*="message"]',
                        '.message-content',
                        '[role="assistant"]',
                        '.prose',
                        '.claude-response'
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
                                            logging.info(f"Captured Claude response ({len(text_content)} chars)")
                                            
                                            # Save response to file
                                            with open(output_file, 'w', encoding='utf-8') as f:
                                                f.write(f"Prompt: {prompt}\n\n")
                                                f.write(f"Response from Anthropic Claude:\n")
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
                    await page.screenshot(path="./debug/claude_no_response.png")
                else:
                    logging.error("No send button found")
                    await page.screenshot(path="./debug/claude_no_send.png")
            else:
                logging.error("Could not find input field")
                await page.screenshot(path="./debug/claude_no_input.png")
                
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            await page.screenshot(path="./debug/claude_error.png")
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
    success = asyncio.run(claude_chat_automation())
    if success:
        logging.info("Claude automation completed successfully")
    else:
        logging.error("Claude automation failed")