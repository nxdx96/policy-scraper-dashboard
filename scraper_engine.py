"""
Web Scraping Engine with Macro Support
Supports predefined macros for common Selenium operations
"""

import os
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


class ScrapingMacros:
    """Predefined macros for common scraping operations"""
    
    @staticmethod
    def click_element(driver, selector, selector_type="css"):
        """
        CLICK_ELEMENT(selector, type='css')
        Clicks an element found by the given selector
        """
        try:
            wait = WebDriverWait(driver, 10)
            if selector_type.lower() == 'css':
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elif selector_type.lower() == 'xpath':
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            elif selector_type.lower() == 'id':
                element = wait.until(EC.element_to_be_clickable((By.ID, selector)))
            elif selector_type.lower() == 'class':
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector)))
            else:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            
            element.click()
            return {"status": "success", "message": f"Clicked element: {selector}"}
        except TimeoutException:
            return {"status": "error", "message": f"Timeout waiting for element: {selector}"}
        except Exception as e:
            return {"status": "error", "message": f"Error clicking element: {str(e)}"}

    @staticmethod
    def scroll_page(driver, direction="down", pixels=None):
        """
        SCROLL_PAGE(direction='down', pixels=500)
        Scrolls the page in the specified direction
        """
        try:
            if pixels is None:
                pixels = 500
            
            if direction.lower() == "down":
                driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction.lower() == "up":
                driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction.lower() == "top":
                driver.execute_script("window.scrollTo(0, 0);")
            elif direction.lower() == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(1)  # Wait for scroll to complete
            return {"status": "success", "message": f"Scrolled {direction} by {pixels}px"}
        except Exception as e:
            return {"status": "error", "message": f"Error scrolling: {str(e)}"}

    @staticmethod
    def save_html(driver, filename=None, job_id=None):
        """
        SAVE_HTML(filename='page.html')
        Saves the current page HTML to a file
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                job_prefix = f"job_{job_id}_" if job_id else ""
                filename = f"{job_prefix}scraped_{timestamp}.html"
            
            # Create downloads directory if it doesn't exist
            downloads_dir = "downloads"
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            filepath = os.path.join(downloads_dir, filename)
            
            # Get page source and save
            html_content = driver.page_source
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {"status": "success", "message": f"HTML saved to: {filepath}", "file": filepath}
        except Exception as e:
            return {"status": "error", "message": f"Error saving HTML: {str(e)}"}

    @staticmethod
    def wait_seconds(driver, seconds=2):
        """
        WAIT(seconds=2)
        Waits for the specified number of seconds
        """
        try:
            time.sleep(float(seconds))
            return {"status": "success", "message": f"Waited {seconds} seconds"}
        except Exception as e:
            return {"status": "error", "message": f"Error waiting: {str(e)}"}

    @staticmethod
    def extract_text(driver, selector, selector_type="css"):
        """
        EXTRACT_TEXT(selector, type='css')
        Extracts text from an element
        """
        try:
            wait = WebDriverWait(driver, 10)
            if selector_type.lower() == 'css':
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif selector_type.lower() == 'xpath':
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elif selector_type.lower() == 'id':
                element = wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif selector_type.lower() == 'class':
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
            else:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            text = element.text
            return {"status": "success", "message": f"Extracted text from {selector}", "data": text}
        except TimeoutException:
            return {"status": "error", "message": f"Timeout waiting for element: {selector}"}
        except Exception as e:
            return {"status": "error", "message": f"Error extracting text: {str(e)}"}


class ScrapingEngine:
    """Main scraping engine that executes macro-based instructions"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.macros = ScrapingMacros()
        self.results = []

    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return {"status": "success", "message": "WebDriver initialized"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to initialize WebDriver: {str(e)}"}

    def parse_macro(self, instruction):
        """Parse a macro instruction and extract command and parameters"""
        instruction = instruction.strip()
        
        # Match macro pattern: COMMAND(param1='value1', param2='value2')
        pattern = r"(\w+)\((.*?)\)"
        match = re.match(pattern, instruction)
        
        if not match:
            return None
        
        command = match.group(1).upper()
        params_str = match.group(2)
        
        # Parse parameters
        params = {}
        if params_str:
            # Simple parameter parsing (can be enhanced)
            param_pattern = r"(\w+)=(['\"]?)(.*?)\2(?:,|$)"
            for param_match in re.finditer(param_pattern, params_str):
                key = param_match.group(1)
                value = param_match.group(3)
                params[key] = value
        
        return {"command": command, "params": params}

    def execute_instruction(self, instruction, job_id=None):
        """Execute a single macro instruction"""
        parsed = self.parse_macro(instruction)
        
        if not parsed:
            return {"status": "error", "message": f"Invalid instruction format: {instruction}"}
        
        command = parsed["command"]
        params = parsed["params"]
        
        try:
            if command == "CLICK_ELEMENT":
                selector = params.get("selector", "")
                selector_type = params.get("type", "css")
                return self.macros.click_element(self.driver, selector, selector_type)
            
            elif command == "SCROLL_PAGE":
                direction = params.get("direction", "down")
                pixels = int(params.get("pixels", 500))
                return self.macros.scroll_page(self.driver, direction, pixels)
            
            elif command == "SAVE_HTML":
                filename = params.get("filename")
                return self.macros.save_html(self.driver, filename, job_id)
            
            elif command == "WAIT":
                seconds = float(params.get("seconds", 2))
                return self.macros.wait_seconds(self.driver, seconds)
            
            elif command == "EXTRACT_TEXT":
                selector = params.get("selector", "")
                selector_type = params.get("type", "css")
                return self.macros.extract_text(self.driver, selector, selector_type)
            
            else:
                return {"status": "error", "message": f"Unknown command: {command}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Error executing {command}: {str(e)}"}

    def run_scraping_job(self, job_data):
        """Execute a complete scraping job"""
        job_id = job_data.get("id")
        url = job_data.get("url")
        instructions = job_data.get("selenium_instructions", "")
        
        self.results = []
        
        # Setup driver
        setup_result = self.setup_driver()
        if setup_result["status"] == "error":
            return setup_result
        
        try:
            # Navigate to URL
            self.driver.get(url)
            self.results.append({"status": "success", "message": f"Navigated to: {url}"})
            
            # Execute instructions line by line
            if instructions:
                lines = [line.strip() for line in instructions.split('\n') if line.strip()]
                
                for line in lines:
                    # Skip comments
                    if line.startswith('#') or line.startswith('//'):
                        continue
                    
                    result = self.execute_instruction(line, job_id)
                    self.results.append({
                        "instruction": line,
                        "result": result
                    })
                    
                    # Stop execution if there's an error
                    if result["status"] == "error":
                        break
            
            return {
                "status": "success", 
                "message": f"Scraping job {job_id} completed",
                "results": self.results
            }
        
        except Exception as e:
            return {"status": "error", "message": f"Error during scraping: {str(e)}"}
        
        finally:
            if self.driver:
                self.driver.quit()

    def get_macro_documentation(self):
        """Return documentation for available macros"""
        return {
            "CLICK_ELEMENT": {
                "description": "Clicks an element on the page",
                "syntax": "CLICK_ELEMENT(selector='css_selector', type='css')",
                "parameters": {
                    "selector": "CSS selector, XPath, ID, or class name",
                    "type": "Selector type: 'css', 'xpath', 'id', 'class' (default: 'css')"
                },
                "example": "CLICK_ELEMENT(selector='button.submit', type='css')"
            },
            "SCROLL_PAGE": {
                "description": "Scrolls the page in the specified direction",
                "syntax": "SCROLL_PAGE(direction='down', pixels=500)",
                "parameters": {
                    "direction": "'down', 'up', 'top', 'bottom' (default: 'down')",
                    "pixels": "Number of pixels to scroll (default: 500)"
                },
                "example": "SCROLL_PAGE(direction='down', pixels=800)"
            },
            "SAVE_HTML": {
                "description": "Saves the current page HTML to a file",
                "syntax": "SAVE_HTML(filename='page.html')",
                "parameters": {
                    "filename": "Output filename (optional, auto-generated if not provided)"
                },
                "example": "SAVE_HTML(filename='scraped_data.html')"
            },
            "WAIT": {
                "description": "Waits for the specified number of seconds",
                "syntax": "WAIT(seconds=2)",
                "parameters": {
                    "seconds": "Number of seconds to wait (default: 2)"
                },
                "example": "WAIT(seconds=5)"
            },
            "EXTRACT_TEXT": {
                "description": "Extracts text from an element",
                "syntax": "EXTRACT_TEXT(selector='css_selector', type='css')",
                "parameters": {
                    "selector": "CSS selector, XPath, ID, or class name",
                    "type": "Selector type: 'css', 'xpath', 'id', 'class' (default: 'css')"
                },
                "example": "EXTRACT_TEXT(selector='h1.title', type='css')"
            }
        }