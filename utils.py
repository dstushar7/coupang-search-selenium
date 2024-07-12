from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip

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
        f.write("\n")
        f.write("\n")
        f.write(f"Product {product_number}\n")
        f.write("-------\n")
        f.write(f"URL: {result['Product URL']}\n")
        f.write(f"Title: {result['Product Title']}\n")
        f.write(f"Price: {result['Product Price']}\n")
        f.write(f"Image URL: {result['Product Image URL']}\n")
        if 'Extension Products' in result:
            for ext_product in result['Extension Products']:
                f.write("----------------\n")
                f.write(f"URL: {ext_product['Extension URL']}\n")
                f.write(f"Title: {ext_product['Extension Title']}\n")
                f.write(f"Price: {ext_product['Extension Price']}\n")
                f.write(f"Margin: {ext_product['Extension Margin']}\n")
                f.write(f"Image URL: {ext_product['Extension Image URL']}\n")

def extract_extension_products_from_table(driver, main_product_price):
    """
    Extract information of extension products from the table.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
        main_product_price (float): Price of the main product.
    
    Returns:
        List[dict]: List of dictionaries containing extension products information.
    """
    extension_products = []
    table_rows_selector = "//table/tbody/tr"
    table_rows = driver.find_elements(By.XPATH, table_rows_selector)
    
    for row in table_rows:
        if len(extension_products) >= 5:
            break
        try:
            extension_image = row.find_element(By.XPATH, ".//img")
            extension_image_url = extension_image.get_attribute("data-src")
            extension_title = row.find_element(By.XPATH, ".//div[@class='ap-copy-content__txt']").text
            extension_price = float(row.find_element(By.XPATH, ".//td[3]/div").text.strip())
            extension_sales_volume = int(row.find_element(By.XPATH, ".//td[4]/div").text.strip())
            
            extension_margin = (main_product_price * 0.89) - (extension_price * 250)

            if extension_margin >= 4000 and extension_sales_volume >= 2:
                # Click the Copy link button
                copy_link_button = row.find_element(By.XPATH, ".//button[contains(@class, 'ap-button') and contains(@class, 'ap-button--primary') and not(contains(@class, 'ap-button--s'))]")
                copy_link_button.click()
                time.sleep(1)  # Wait for the clipboard to update

                # Fetch the copied value from the clipboard
                extension_url = pyperclip.paste()
                
                extension_products.append({
                    "Extension Title": extension_title,
                    "Extension Price": extension_price,
                    "Extension Sales Volume": extension_sales_volume,
                    "Extension Margin": extension_margin,
                    "Extension Image URL": extension_image_url,
                    "Extension URL": extension_url
                })
        except Exception as e:
            print(f"Could not extract extension product information: {e}")

    return extension_products

def hover_and_click_icons(driver, filename, start_product_number=1):
    """
    Hover over each product image to reveal and click the extension icons, then extract extension product details.
    
    Args:
        driver (WebDriver): Initialized WebDriver.
        start_product_number (int): The starting number for the product.
    """
    product_selector = "//ul[@id='productList']//li"
    products = driver.find_elements(By.XPATH, product_selector)
    # first_time = True
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to be present

    product_number = start_product_number
    for product in products:
        try:
            image = product.find_element(By.XPATH, ".//img")
            actions.move_to_element(image).perform()
            
            icon_xpath = ".//i[contains(@class, 'ap-sbi-btn-search__icon') and contains(@class, 'ap-icon-search')]"
            icon = wait.until(EC.presence_of_element_located((By.XPATH, icon_xpath)))
            icon.click()
            time.sleep(10)
            
            filter_button_xpath = "//button[contains(@class, 'ap-show-export-products-modal')]"
            filter_button = wait.until(EC.presence_of_element_located((By.XPATH, filter_button_xpath)))
            filter_button.click()
            time.sleep(5)
            
            # sales_volume_header_xpath = "//div[@class='ap-table']//table//thead//tr//th[4]"
            # sales_volume_header = wait.until(EC.presence_of_element_located((By.XPATH, sales_volume_header_xpath)))
            # sales_volume_header.click()
            # time.sleep(2)
            # if first_time:
            #     sales_volume_header.click()
            #     first_time = False
            
            product_url = product.find_element(By.XPATH, ".//a").get_attribute("href")
            product_title = product.find_element(By.XPATH, ".//div[contains(@class, 'name')]").text
            product_price = float(product.find_element(By.XPATH, ".//strong[contains(@class, 'price-value')]").text.replace(",", "").strip())
            product_image_url = image.get_attribute("src")
            
            if product_image_url.startswith("//"):
                product_image_url = "https:" + product_image_url

            result = {
                "Product URL": product_url,
                "Product Title": product_title,
                "Product Price": product_price,
                "Product Image URL": product_image_url
            }

            result["Extension Products"] = extract_extension_products_from_table(driver, product_price)

            write_result_to_file(result, filename, product_number)
            
            # Close the filter section of extension modal
            close_button_xpath = "//div[@class='ap-modal-close']"
            close_button = wait.until(EC.presence_of_element_located((By.XPATH, close_button_xpath)))
            close_button.click()
            time.sleep(2)


            # Wait for the close button of extension modal to present and then click it
            close_button_selector = ".//div[contains(@class, 'ap-sbi-aside-btn-close') and contains(@class, 'ap-icon-close-circle')]"
            close_button = wait.until(EC.presence_of_element_located((By.XPATH, close_button_selector)))
            close_button.click()
            time.sleep(2)  # Wait a bit between actions
            product_number += 1
        except Exception as e:
            print(f"Could not click the icon or close button for a product: {e}")


def get_increment(price):
    """
    Get the increment based on the current price.
    
    Args:
        price (int): Current price.

    Returns:
        int: The increment value.
    """
    if price < 65000:
        return 100
    elif price < 80000:
        return 200
    elif price < 100000:
        return 400
    elif price < 130000:
        return 500
    elif price < 150000:
        return 1000
    elif price < 180000:
        return 2000
    elif price < 300000:
        return 5000
    elif price < 400000:
        return 10000
    elif price < 500000:
        return 20000
    else:
        return None  # Stop at prices above the maximum price