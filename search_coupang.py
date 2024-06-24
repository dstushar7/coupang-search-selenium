from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

# Path to your ChromeDriver executable
CHROME_DRIVER_PATH = "./chromedriver.exe"

# Path to your Chrome extension .crx file
EXTENSION_PATH = "./AliPrice-Shopping-Assistant-for-1688.crx"

def create_chrome_options(extension_path):
    """
    Create Chrome options and add the extension.
    
    Args:
        extension_path (str): Path to the Chrome extension .crx file.

    Returns:
        Options: Configured Chrome options.
    """
    chrome_options = Options()
    chrome_options.add_extension(extension_path)
    return chrome_options

def initialize_driver(chrome_driver_path, chrome_options):
    """
    Initialize the Chrome WebDriver with the given options.
    
    Args:
        chrome_driver_path (str): Path to the ChromeDriver executable.
        chrome_options (Options): Configured Chrome options.

    Returns:
        WebDriver: Initialized Chrome WebDriver.
    """
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def close_tutorial_tab(driver):
    """
    Close the tutorial tab if it opens after loading the extension.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
    """
    time.sleep(10)  # Wait for 10 seconds to allow the tutorial tab to open
    
    original_window = driver.current_window_handle
    all_windows = driver.window_handles
    
    for window in all_windows:
        if window != original_window:
            driver.switch_to.window(window)
            driver.close()
    
    driver.switch_to.window(original_window)

def navigate_to_url(driver, url):
    """
    Navigate to the specified URL using the WebDriver.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
        url (str): URL to navigate to.
    """
    driver.get(url)
    time.sleep(5)  # Allow some time for the page to load and extension to initialize

def hover_and_click_icons(driver):
    """
    Hover over each product to reveal and click the extension icons.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
    """
    # Select all product elements
    product_selector = "//ul[@id='productList']//li"
    products = driver.find_elements(By.XPATH, product_selector)
    
    # Initialize ActionChains
    actions = ActionChains(driver)
    
    for product in products:
        # Hover over the product to reveal the icon
        actions.move_to_element(product).perform()
        time.sleep(1)  # Wait a bit to ensure the icon appears
        
        try:
            # Click the revealed icon using the provided XPath
            icon_xpath = ".//i[contains(@class, 'ap-sbi-btn-search__icon') and contains(@class, 'ap-icon-search')]"  # Update to match your specific structure
            icon = driver.find_element(By.XPATH, icon_xpath)
            icon.click()
            time.sleep(1)  # Wait a bit between clicks

            # Click the close button using its class
            close_button_selector = ".ap-sbi-aside-btn-close.ap-icon-close-circle"
            close_button = driver.find_element(By.CSS_SELECTOR, close_button_selector)
            close_button.click()
            time.sleep(1)  # Wait a bit between actions
        except Exception as e:
            print(f"Could not click the icon for a product: {e}")

def main():
    """
    Main function to set up and run the Selenium script.
    """
    search_query = "laptop"
    url = f"https://www.coupang.com/np/search?component=&q={search_query}&channel=user"
    
    chrome_options = create_chrome_options(EXTENSION_PATH)
    driver = initialize_driver(CHROME_DRIVER_PATH, chrome_options)
    
    try:
        close_tutorial_tab(driver)
        navigate_to_url(driver, url)
        hover_and_click_icons(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
