from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime
import pytz

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

driver = webdriver.Chrome(options=chrome_options)
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

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

url_list = []

try:
    list_fixtures_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.list-fixtures'))
    )
    first_div_no_class = list_fixtures_div.find_element(By.XPATH, "./div[not(@class)]")
    watch_now_links = first_div_no_class.find_elements(By.CSS_SELECTOR, 'a.b-btn.b-btn-watch-red.is-rounded.text-xs.link-nested')

    # Populate url_list with match details
    for link in watch_now_links:
        match_url = link.get_attribute('href')
        url_list.append({'match_detail': match_url})

    # Iterate over each match URL to find the iframe and match info
    for match in url_list:
        match_url = match['match_detail']
        driver.get(match_url)
        WebDriverWait(driver, 10).until(lambda driver: page_has_loaded(driver))

        # Find the iframe
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
            )
            iframe_src = iframe.get_attribute('src')
            match['iframe_src'] = iframe_src
        except NoSuchElementException:
            match['iframe_src'] = None

        # Find match information
        try:
            match_info_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'match-info-wrapper'))
            )

            # Extract Home Team Name and Logo
            home_team = match_info_div.find_element(By.CSS_SELECTOR, 'div.club-wrapper:first-child span.club-name a').text.strip()
            home_logo = match_info_div.find_element(By.CSS_SELECTOR, 'div.club-wrapper:first-child img.club-image').get_attribute('src')

            # Extract Away Team Name and Logo
            away_team = match_info_div.find_element(By.CSS_SELECTOR, 'div.club-wrapper:last-child span.club-name a').text.strip()
            away_logo = match_info_div.find_element(By.CSS_SELECTOR, 'div.club-wrapper:last-child img.club-image').get_attribute('src')

            # Add to the match dictionary
            match['Home'] = home_team
            match['Home_Logo'] = home_logo
            match['Away'] = away_team
            match['Away_Logo'] = away_logo
        except NoSuchElementException:
            # If match info is not found, add None
            match.update({'Home': None, 'Home_Logo': None, 'Away': None, 'Away_Logo': None})

except NoSuchElementException:
    print("There is No Live Match.")

# Extract the token from the first iframe URL
token_value = ""
if url_list and 'iframe_src' in url_list[0]:
    first_iframe_url = url_list[0]['iframe_src']
    token_start_index = first_iframe_url.find('&token=')
    if token_start_index != -1:
        token_value = first_iframe_url[token_start_index:]

# Check if the token is not empty before exporting to JSON
if token_value:
    # Get the current time in GMT+7
    timezone = pytz.timezone('Etc/GMT-7')
    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

    # Prepare the data to be dumped into JSON
    data_to_dump = {
        "matches": url_list,
        "token": token_value,  # Add the token here
        "timestamp": current_time
    }

    # Write the data to the JSON file
    with open('livestream.json', 'w') as json_file:
        json.dump(data_to_dump, json_file, indent=4)

driver.quit()