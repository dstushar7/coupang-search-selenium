from utils import create_chrome_options, initialize_driver, close_tutorial_tab, navigate_to_url, hover_and_click_icons, get_increment

# Path to your ChromeDriver executable
CHROME_DRIVER_PATH = "./chromedriver.exe"

# Path to your Chrome extension .crx file
EXTENSION_PATH = "./AliPrice-Shopping-Assistant-for-1688.crx"

def main():
    # Define the parameters for the search
    search_query = "laptop"
    rating = 4
    list_size = 72 # Lowest is 10, highest is 72
    min_page = 1 
    max_page = 12 # Number of pages to be traversed

    # Initialize the starting price and maximum price
    min_price = 30000
    max_dynamic_price = 500000  # Change this value as needed for different maximum price limits, 500000 is the maximum.
    max_price = min_price + get_increment(min_price)

    # Create Chrome options and initialize the driver
    chrome_options = create_chrome_options(EXTENSION_PATH)
    driver = initialize_driver(CHROME_DRIVER_PATH, chrome_options)

    try:
        # Close any tutorial tabs that might open
        close_tutorial_tab(driver)
        
        # Loop through the price ranges and pages
        while min_price < max_dynamic_price:
            for page in range(min_page, max_page + 1):
                url = (
                    f"https://www.coupang.com/np/search?q={search_query}&"
                    f"filterSetByUser=true&channel=user&isPriceRange=true&minPrice={min_price}&maxPrice={max_price}&"
                    f"page={page}&rating={rating}&listSize={list_size}"
                )
                navigate_to_url(driver, url)
                hover_and_click_icons(driver, search_query)
            
            # Update the price range
            min_price = max_price
            increment = get_increment(min_price)
            if increment is None or max_price >= max_dynamic_price:
                break  # Stop if there is no valid increment or if the max price limit is reached
            max_price = min_price + increment
    finally:
        # Close the driver after completing the tasks
        driver.quit()

if __name__ == "__main__":
    main()
