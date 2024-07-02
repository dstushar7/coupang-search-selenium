from utils import create_chrome_options, initialize_driver, close_tutorial_tab, navigate_to_url, hover_and_click_icons

# Path to your ChromeDriver executable
CHROME_DRIVER_PATH = "./chromedriver.exe"

# Path to your Chrome extension .crx file
EXTENSION_PATH = "./AliPrice-Shopping-Assistant-for-1688.crx"

def main():
    # Define the parameters for the search
    search_query = "laptop"
    min_price = 30000
    max_price = 31000
    rating = 4
    list_size = 72

    # Create Chrome options and initialize the driver
    chrome_options = create_chrome_options(EXTENSION_PATH)
    driver = initialize_driver(CHROME_DRIVER_PATH, chrome_options)

    try:
        # Close any tutorial tabs that might open
        close_tutorial_tab(driver)
        
        # Loop through the pages and perform the necessary actions
        for page in range(1, 12):
            url = (
                f"https://www.coupang.com/np/search?q={search_query}&"
                f"filterSetByUser=true&channel=user&isPriceRange=true&minPrice={min_price}&maxPrice={max_price}&"
                f"page={page}&rating={rating}&listSize={list_size}"
            )
            navigate_to_url(driver, url)
            hover_and_click_icons(driver, search_query)
    finally:
        # Close the driver after completing the tasks
        driver.quit()

if __name__ == "__main__":
    main()
