from selenium import webdriver
from time import sleep  # Correct import for sleep

# Fetch page using Selenium
def fetch_website_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.javascript": 1
    })
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        sleep(5)  # Correct usage of sleep from the time module
        html_content = driver.page_source
        return html_content
    finally:
        driver.quit()
