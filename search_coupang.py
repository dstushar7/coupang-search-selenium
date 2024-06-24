from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    driver.maximize_window()
    return driver

def close_tutorial_tab(driver):
    """
    Close the tutorial tab if it opens after loading the extension.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
    """
    time.sleep(5)  # Wait for 5 seconds to allow the tutorial tab to open
    
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
    time.sleep(2)  # Allow some time for the page to load and extension to initialize

def hover_and_click_icons(driver):
    """
    Hover over each product image to reveal and click the extension icons.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
    """
    # Select all product elements
    product_selector = "//ul[@id='productList']//li"
    products = driver.find_elements(By.XPATH, product_selector)
    
    # Initialize ActionChains
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to be present
    
    count = 0

    for product in products:
        try:
            # Hover over the product image to reveal the icon
            image = product.find_element(By.XPATH, ".//img")
            actions.move_to_element(image).perform()
            
            # Wait for the icon to be present and then click it
            icon_xpath = ".//i[contains(@class, 'ap-sbi-btn-search__icon') and contains(@class, 'ap-icon-search')]"
            icon = wait.until(EC.presence_of_element_located((By.XPATH, icon_xpath)))
            icon.click()
            time.sleep(1)  # Wait a bit for the close button to appear
            
            # Wait for the close button to be present and then click it
            close_button_selector = ".//div[contains(@class, 'ap-sbi-aside-btn-close') and contains(@class, 'ap-icon-close-circle')]"
            close_button = wait.until(EC.presence_of_element_located((By.XPATH, close_button_selector)))
            close_button.click()
            time.sleep(1)  # Wait a bit between actions

            count += 1
        except Exception as e:
            print(f"Could not click the icon or close button for a product: {e}")

    return count

def main():
    """
    Main function to set up and run the Selenium script.
    """
    search_query = "laptop"
    min_price = 30000
    max_price = 31000
    rating = 4
    list_size = 72
    
    chrome_options = create_chrome_options(EXTENSION_PATH)
    driver = initialize_driver(CHROME_DRIVER_PATH, chrome_options)
    
    try:
        close_tutorial_tab(driver)
        
        total_clicks = 0
        for page in range(1, 12):
            url = (f"https://www.coupang.com/np/search?q={search_query}&"
                   f"isPriceRange=true&minPrice={min_price}&maxPrice={max_price}&"
                   f"page={page}&rating={rating}&listSize={list_size}")
            navigate_to_url(driver, url)
            clicks = hover_and_click_icons(driver)
            total_clicks += clicks
            print(f"Page {page}: Clicked {clicks} icons")
        
        print(f"Total icons clicked: {total_clicks}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()