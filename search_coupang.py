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
    driver.delete_all_cookies()
    driver.get(url)
    time.sleep(2)  # Allow some time for the page to load and extension to initialize

def write_result_to_file(result, filename, product_number):
    """
    Append the extracted product information to a text file.
    
    Args:
        result (dict): Dictionary containing product information.
        filename (str): Name of the file to write the results to.
    """
    filename += ".txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"Product {product_number}\n")
        f.write("------\n")
        f.write(f"URL: {result['Product URL']}\n")
        f.write(f"Title: {result['Product Title']}\n")
        f.write(f"Price: {result['Product Price']}\n")
        f.write(f"Image URL: {result['Product Image URL']}\n")
        f.write("\n")
        if 'Extension Products' in result:
            for ext_product in result['Extension Products']:
                f.write("------\n")
                f.write(f"  Extension Product URL: {ext_product['Extension URL']}\n")
                f.write(f"  Extension Product Title: {ext_product['Extension Title']}\n")
                f.write(f"  Extension Product Price: {ext_product['Extension Price']}\n")
                f.write(f"  Extension Product Margin: {ext_product['Extension Margin']}\n")
                f.write(f"  Extension Product Image URL: {ext_product['Extension Image URL']}\n")
                f.write("\n")

def extract_extension_products(driver, main_product_price):
    """
    Extract information of extension products.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
        main_product_price (float): Price of the main product.
    
    Returns:
        List[dict]: List of dictionaries containing extension products information.
    """
    extension_products = []
    extension_product_selector = "//div[contains(@class, 'ap-list-cards--panel') and contains(@class, 'alipriceAlibabaCN')]//div[@class='ap-list-card']"
    extension_product_elements = driver.find_elements(By.XPATH, extension_product_selector)
    
    for ext_product in extension_product_elements:
        try:
            # extension_url = ext_product.find_element(By.XPATH, ".//a").get_attribute("href")
            extension_url = "TEST"
            extension_title = ext_product.find_element(By.XPATH, ".//div[contains(@class, 'ap-product-title')]").text
            extension_price = float(ext_product.find_element(By.XPATH, ".//div[contains(@class, 'ap-product-price')]").text.replace("¥", "").strip())
            extension_image_url = ext_product.find_element(By.XPATH, ".//img").get_attribute("large")
            
            # Calculate margin
            extension_margin = (main_product_price * 0.89) - (extension_price * 250)

            extension_products.append({
                "Extension URL": extension_url,
                "Extension Title": extension_title,
                "Extension Price": extension_price,
                "Extension Margin": extension_margin,
                "Extension Image URL": extension_image_url
            })
        except Exception as e:
            print(f"Could not extract extension product information: {e}")

    return extension_products

def hover_and_click_icons(driver, searchquery, start_product_number=1):
    """
    Hover over each product image to reveal and click the extension icons.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
        start_product_number (int): The starting number for the product.
    """
    # Select all product elements
    product_selector = "//ul[@id='productList']//li"
    products = driver.find_elements(By.XPATH, product_selector)
    
    # Initialize ActionChains
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to be present

    # Loop over each product
    product_number = start_product_number
    for product in products:
        try:
            # Hover over the product image to reveal the icon
            image = product.find_element(By.XPATH, ".//img")
            actions.move_to_element(image).perform()
            
            # Wait for the icon to be present and then click it
            icon_xpath = ".//i[contains(@class, 'ap-sbi-btn-search__icon') and contains(@class, 'ap-icon-search')]"
            icon = wait.until(EC.presence_of_element_located((By.XPATH, icon_xpath)))
            icon.click()
            time.sleep(10)  # Wait a bit for the extension products to appear
            
            # Extract main product information
            product_url = product.find_element(By.XPATH, ".//a").get_attribute("href")
            product_title = product.find_element(By.XPATH, ".//div[contains(@class, 'name')]").text
            product_price = float(product.find_element(By.XPATH, ".//strong[contains(@class, 'price-value')]").text.replace(",", "").strip())
            product_image_url = image.get_attribute("src")
            
            # Format the image URL correctly
            if product_image_url.startswith("//"):
                product_image_url = "https:" + product_image_url

            result = {
                "Product URL": product_url,
                "Product Title": product_title,
                "Product Price": product_price,
                "Product Image URL": product_image_url
            }

            # Extract extension products information
            result["Extension Products"] = extract_extension_products(driver, product_price)

            # Write the result to file
            write_result_to_file(result, searchquery, product_number)

            # Wait for the close button to be present and then click it
            close_button_selector = ".//div[contains(@class, 'ap-sbi-aside-btn-close') and contains(@class, 'ap-icon-close-circle')]"
            close_button = wait.until(EC.presence_of_element_located((By.XPATH, close_button_selector)))
            close_button.click()
            time.sleep(2)  # Wait a bit between actions

            product_number += 1
        except Exception as e:
            print(f"Could not click the icon or close button for a product: {e}")

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
        
        for page in range(1, 12):
            url = (f"https://www.coupang.com/np/search?q={search_query}&"
                   f"filterSetByUser=true&channel=user&isPriceRange=true&minPrice={min_price}&maxPrice={max_price}&"
                   f"page={page}&rating={rating}&listSize={list_size}")
            navigate_to_url(driver, url)
            hover_and_click_icons(driver, search_query)
            time.sleep(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
