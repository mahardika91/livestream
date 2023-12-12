from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime
import pytz
import os

def page_has_loaded(driver):
    return driver.execute_script("return document.readyState;") == "complete"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

url = "https://scorevisit.com/login"
username = "itctrlr@gmail.com"
password = "Ungu4150645#"

PATH = "C:\\Users\\Administrator1\\Desktop\\scrape\\livestream\\chromedriver.exe"

# Create a Service object with the path to chromedriver
service = Service(executable_path=PATH)

# Initialize the Chrome WebDriver with the specified options
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(url)


WebDriverWait(driver, 10).until(lambda driver: page_has_loaded(driver))

username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Email address or username"]'))
)
username_field.send_keys(username)

password_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
)
password_field.send_keys(password)

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//button[@class="btn-submit"]'))
)
login_button.click()

url_list = []
token_value = ""

try:
    list_fixtures_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.list-fixtures'))
    )
    first_div_no_class = list_fixtures_div.find_element(By.XPATH, "./div[not(@class)]")
    watch_now_links = first_div_no_class.find_elements(By.CSS_SELECTOR, 'a.b-btn.b-btn-watch-red.is-rounded.text-xs.link-nested')

    # Get the first match URL
    if watch_now_links:
        first_match_url = watch_now_links[0].get_attribute('href')
        driver.get(first_match_url)
        WebDriverWait(driver, 10).until(lambda driver: page_has_loaded(driver))

        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
            )
            iframe_src = iframe.get_attribute('src')
            token_start_index = iframe_src.find('&token=')
            if token_start_index != -1:
                token_end_index = iframe_src.find('&', token_start_index + 1)
                if token_end_index == -1:
                    token_value = iframe_src[token_start_index + len('&token='):]
                else:
                    token_value = iframe_src[token_start_index + len('&token='):token_end_index]
        except NoSuchElementException:
            token_value = ""

except NoSuchElementException:
    print("There is No Live Match.")

# Check if token_value is empty before writing to JSON
if token_value:
    old_token_value = None

    # Check if the JSON file already exists
    if os.path.exists('livestream.json'):
        with open('livestream.json', 'r') as json_file:
            data = json.load(json_file)
            old_token_value = data.get("token", None)

    # Write to JSON only if the new token is different from the old token
    if token_value != old_token_value:
        # Get the current time in GMT+7
        timezone = pytz.timezone('Etc/GMT-7')
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the data to be dumped into JSON
        data_to_dump = {
            "token": token_value,  # Add the new token here
            "timestamp": current_time
        }

        # Write the new data to the JSON file
        with open('livestream.json', 'w') as json_file:
            json.dump(data_to_dump, json_file, indent=4)

driver.quit()