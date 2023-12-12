from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import datetime
import pytz
import os
import subprocess
import time

def open_website_and_extract_iframe():
    # Set up Chrome driver options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

    # Set up Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the URL
    driver.get("https://scorevisit.com/")

    # Initialize WebDriverWait
    wait = WebDriverWait(driver, 10)

    extracted_token = None
    try:
        watch_now_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Watch Now')]")))
        link = watch_now_link.get_attribute('href')
        driver.get(link)
        
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe_src = iframe.get_attribute('src')
        
        # Extracting the token from the iframe_src URL
        token_start = iframe_src.find("&token=") + len("&token=")
        if token_start > len("&token="):
            token_end = iframe_src.find("&", token_start)
            extracted_token = iframe_src[token_start:] if token_end == -1 else iframe_src[token_start:token_end]
        else:
            raise Exception("Token not found in iframe source")      
            print("Error finding iframe or extracting token:", iframe_error)
     
    except Exception as watch_now_error:
        print("Error finding 'Watch Now' link:", watch_now_error)

    if extracted_token:
        current_time = datetime.datetime.now(pytz.timezone('Asia/Bangkok'))
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        filename = "livestream.json"
        old_token = None
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                old_data = json.load(file)
                old_token = old_data.get("token")
        if old_token != extracted_token:
            output_data = {"token": extracted_token, "timestamp": formatted_time}
            with open(filename, 'w') as file:
                json.dump(output_data, file, indent=4)
            print(f"New token and timestamp extracted and saved as JSON in {filename}.")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "fixture"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Changes pushed to the repository.")
        else:
            print("Token is unchanged. No new file exported.")
    else:
        print("No valid token extracted.")

    # Close the browser
    driver.quit()

# Main loop to run the function indefinitely with a 10-second delay
while True:
    try:
        os.system('cls')  # Clear the console for Windows
        open_website_and_extract_iframe()
        print("Script executed successfully. Waiting 10 seconds to re-run...")
    except Exception as e:
        print(f"An error occurred: {e}. Waiting 10 seconds to re-run...")
    time.sleep(10)
