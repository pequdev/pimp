from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

async def search_google(query, preferred_domain=None):
    try:
        driver = webdriver.Chrome()
        driver.get("https://www.google.com")

        search_box = driver.find_element_by_name("q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(2)

        results = driver.find_elements_by_css_selector('h3')
        for result in results:
            link_element = result.find_element_by_xpath('..')
            link = link_element.get_attribute('href')
            if preferred_domain in link:
                driver.quit()
                return link

        driver.quit()
        return -1
    except Exception as e:
        return -1