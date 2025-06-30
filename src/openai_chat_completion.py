#!/usr/bin/env python3
"""
OpenAI ChatGPT Chat Completion Automation
Automates browser interactions with ChatGPT to:
1. Navigate to https://chatgpt.com
2. Submit a text prompt
3. Capture and save the AI response
"""

import asyncio
import os
import time
import logging
from pathlib import Path
from playwright.async_api import async_playwright

async def openai_chat_automation(output_dir=None, prompt=None):
    """Main automation function for OpenAI ChatGPT"""
    
    # Set up paths with defaults
    if output_dir is None:
        output_dir = Path("./data/output")
    else:
        output_dir = Path(output_dir)
    
    if prompt is None:
        prompt = "Explain the concept of artificial intelligence in simple terms"
    
    output_file = output_dir / "openai-text-completion.txt"
    
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
            logging.info("Navigating to ChatGPT")
            await page.goto("https://chatgpt.com/", timeout=60000)
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Look for login requirements or proceed directly
            login_selectors = [
                'button:has-text("Log in")',
                'a:has-text("Log in")',
                'button:has-text("Sign up")'
            ]
            
            # Check if login is required
            needs_login = False
            for selector in login_selectors:
                try:
                    login_element = await page.wait_for_selector(selector, timeout=3000)
                    if login_element:
                        logging.warning("Login required for ChatGPT - trying guest mode or alternative")
                        needs_login = True
                        break
                except:
                    continue
            
            # Look for prompt input
            logging.info("Looking for chat input")
            input_selectors = [
                'textarea[placeholder*="Message"]',
                'textarea[data-id*="chat"]',
                'div[contenteditable="true"]',
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
                    'button[data-testid="send-button"]',
                    'button:has-text("Send")',
                    'button[type="submit"]',
                    'svg[data-icon="send"]',
                    'button[aria-label*="Send"]'
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
                    logging.info("Waiting for AI response")
                    await asyncio.sleep(10)  # Wait for initial response
                    
                    # Look for response elements
                    response_selectors = [
                        '[data-message-author-role="assistant"]',
                        '.markdown',
                        '[data-testid*="conversation"]',
                        '.conversation-turn',
                        '.message-content'
                    ]
                    
                    response_found = False
                    for selector in response_selectors:
                        try:
                            # Wait for response to appear and complete
                            await asyncio.sleep(5)  # Additional wait for response completion
                            
                            response_elements = await page.query_selector_all(selector)
                            if response_elements:
                                logging.info(f"Found {len(response_elements)} response elements")
                                
                                # Get the last response (most recent)
                                for element in response_elements[-3:]:  # Check last few responses
                                    try:
                                        text_content = await element.text_content()
                                        if text_content and len(text_content.strip()) > 50:
                                            logging.info(f"Captured response ({len(text_content)} chars)")
                                            
                                            # Save response to file
                                            with open(output_file, 'w', encoding='utf-8') as f:
                                                f.write(f"Prompt: {prompt}\n\n")
                                                f.write(f"Response from OpenAI ChatGPT:\n")
                                                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                                                f.write(text_content.strip())
                                            
                                            logging.info(f"Saved response to: {output_file}")
                                            return True
                                    except Exception as e:
                                        logging.error(f"Error extracting text: {e}")
                                        continue
                                
                                response_found = True
                                break
                        except Exception as e:
                            logging.error(f"Error with selector {selector}: {e}")
                            continue
                    
                    if not response_found:
                        logging.warning("No response found, taking screenshot for debug")
                        await page.screenshot(path="./debug/openai_no_response.png")
                else:
                    logging.error("No send button found")
                    await page.screenshot(path="./debug/openai_no_send.png")
            else:
                logging.error("Could not find input field")
                await page.screenshot(path="./debug/openai_no_input.png")
                
        except Exception as e:
            logging.error(f"Error during automation: {e}")
            await page.screenshot(path="./debug/openai_error.png")
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
    success = asyncio.run(openai_chat_automation())
    if success:
        logging.info("OpenAI ChatGPT automation completed successfully")
    else:
        logging.error("OpenAI ChatGPT automation failed")