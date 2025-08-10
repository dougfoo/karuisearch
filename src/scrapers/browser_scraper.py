"""
Browser-based scraper for JavaScript-heavy sites using Selenium
"""
import time
import random
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, InvalidSessionIdException
import logging

from .base_scraper import AbstractPropertyScraper, PropertyData

logger = logging.getLogger(__name__)

class BrowserScraper(AbstractPropertyScraper):
    """Base class for browser-based scrapers using Selenium"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.driver = None
        self.wait_timeout = config.get('wait_timeout', 10)
        self.page_load_timeout = config.get('page_load_timeout', 30)
        self.headless = config.get('headless', True)
        
    def setup_browser(self):
        """Setup Chrome browser with stability and stealth options"""
        chrome_options = Options()
        
        # Stealth options to avoid detection
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # PHASE 1.1: Browser Stability Improvements
        # Memory and stability optimizations
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=8192')  # 8GB memory limit
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        # Additional stability flags
        chrome_options.add_argument('--disable-crash-reporter')
        chrome_options.add_argument('--disable-in-process-stack-traces')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')  # Suppress console logs
        
        # Mimic real browser
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Speed optimization
        
        # Additional stealth measures
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2  # Block notifications
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # Try to create driver (will use system Chrome)
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(5)
            
            logger.info("Browser setup successful")
            return True
            
        except WebDriverException as e:
            logger.error(f"Failed to setup browser: {e}")
            logger.info("Make sure Chrome browser is installed")
            return False
            
    def close_browser(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
                
    def navigate_to_page(self, url: str) -> bool:
        """Navigate to a page with error handling"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Add human-like delay
            self.simulate_human_delay()
            
            # Check if page loaded successfully
            if "error" in self.driver.title.lower() or "404" in self.driver.title:
                logger.warning(f"Page might have failed to load: {self.driver.title}")
                return False
                
            return True
            
        except TimeoutException:
            logger.error(f"Page load timeout for: {url}")
            return False
        except WebDriverException as e:
            logger.error(f"Navigation error for {url}: {e}")
            return False
            
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> Optional[object]:
        """Wait for an element to be present"""
        timeout = timeout or self.wait_timeout
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            logger.debug(f"Element not found: {by}={value}")
            return None
            
    def wait_for_elements(self, by: By, value: str, timeout: int = None) -> List:
        """Wait for elements to be present"""
        timeout = timeout or self.wait_timeout
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            logger.debug(f"Elements not found: {by}={value}")
            return []
            
    def safe_click(self, element) -> bool:
        """Safely click an element with retry"""
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.simulate_human_delay(0.5, 1.0)
            
            # Try to click
            element.click()
            self.simulate_human_delay()
            return True
            
        except Exception as e:
            logger.debug(f"Click failed: {e}")
            # Try JavaScript click as fallback
            try:
                self.driver.execute_script("arguments[0].click();", element)
                self.simulate_human_delay()
                return True
            except Exception as e2:
                logger.warning(f"Both click methods failed: {e2}")
                return False
                
    def safe_send_keys(self, element, text: str) -> bool:
        """Safely send keys to an element"""
        try:
            element.clear()
            self.simulate_human_delay(0.2, 0.5)
            
            # Type with human-like delays
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            return True
            
        except Exception as e:
            logger.warning(f"Send keys failed: {e}")
            return False
            
    def simulate_human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like random delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def simulate_scrolling(self):
        """Simulate human-like scrolling behavior"""
        try:
            # Random scroll down
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self.simulate_human_delay(0.5, 1.5)
            
            # Random scroll up sometimes
            if random.random() < 0.3:
                scroll_up = random.randint(100, 300)
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_up});")
                self.simulate_human_delay(0.5, 1.0)
                
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {e}")
            
    def get_page_source_after_js(self) -> str:
        """Get page source after JavaScript has executed"""
        try:
            # Wait for potential AJAX/dynamic content
            self.simulate_human_delay(2.0, 4.0)
            
            # Simulate some scrolling to trigger lazy loading
            self.simulate_scrolling()
            
            # Get the page source
            return self.driver.page_source
            
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""
    
    # PHASE 1.2: Enhanced Error Recovery Methods
    def is_browser_crashed(self) -> bool:
        """Check if browser/tab has crashed"""
        if not self.driver:
            return True
            
        try:
            # Try to get current URL - this will fail if tab crashed
            _ = self.driver.current_url
            return False
        except (WebDriverException, InvalidSessionIdException) as e:
            if "tab crashed" in str(e).lower() or "session deleted" in str(e).lower():
                logger.warning(f"Browser crash detected: {e}")
                return True
            return False
        except Exception:
            return False
    
    def recover_from_crash(self) -> bool:
        """Attempt to recover from browser crash by restarting"""
        logger.info("Attempting to recover from browser crash...")
        
        try:
            # Close existing browser
            self.close_browser()
            
            # Wait before restart
            time.sleep(2)
            
            # Setup new browser
            success = self.setup_browser()
            if success:
                logger.info("Browser recovery successful")
                return True
            else:
                logger.error("Browser recovery failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during browser recovery: {e}")
            return False
    
    def safe_execute_with_recovery(self, func, *args, max_retries: int = 2, **kwargs):
        """Execute function with automatic crash recovery"""
        for attempt in range(max_retries + 1):
            try:
                # Check if browser is crashed before execution
                if self.is_browser_crashed():
                    if not self.recover_from_crash():
                        raise WebDriverException("Failed to recover from crash")
                
                # Execute the function
                return func(*args, **kwargs)
                
            except (WebDriverException, InvalidSessionIdException) as e:
                if "tab crashed" in str(e).lower():
                    logger.warning(f"Tab crashed during execution (attempt {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        if self.recover_from_crash():
                            continue
                    raise e
                else:
                    raise e
                    
        return None
            
    def extract_text_safely(self, element) -> str:
        """Safely extract text from a web element"""
        try:
            return element.text.strip()
        except Exception:
            try:
                return element.get_attribute('textContent').strip()
            except Exception:
                return ""
                
    def extract_attribute_safely(self, element, attribute: str) -> str:
        """Safely extract attribute from a web element"""
        try:
            return element.get_attribute(attribute) or ""
        except Exception:
            return ""
            
    def check_for_captcha(self) -> bool:
        """Check if page contains CAPTCHA"""
        captcha_indicators = [
            "captcha", "recaptcha", "bot detection", "human verification"
        ]
        
        page_text = self.driver.page_source.lower()
        return any(indicator in page_text for indicator in captcha_indicators)
        
    def handle_popup_if_present(self):
        """Handle common popups that might interfere"""
        try:
            # Look for common popup close buttons
            popup_selectors = [
                "[aria-label*='close']",
                "[title*='close']",
                ".modal-close",
                ".popup-close",
                ".close-button",
                "button[aria-label='Close']"
            ]
            
            for selector in popup_selectors:
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_button.is_displayed():
                        self.safe_click(close_button)
                        logger.info("Closed popup")
                        return
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            logger.debug(f"Popup handling failed: {e}")
            
    def scrape_listings(self) -> List[PropertyData]:
        """Base implementation - should be overridden by specific scrapers"""
        raise NotImplementedError("Subclasses must implement scrape_listings method")
        
    def __enter__(self):
        """Context manager entry"""
        if self.setup_browser():
            return self
        else:
            raise RuntimeError("Failed to setup browser")
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()