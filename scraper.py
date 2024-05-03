import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
import os

# this gets the user name and pass from the file 
with open("emails.txt", "r") as file:
            email, password = file.readline().strip().split(",")

#this function is made to load cookies If there is no cokkies for the first time it will write a text to hold the cookie
def load_cookies(driver, cookies_name):
    with open(f"cookies/{cookies_name}", "r", encoding="utf-8") as f:
        cookies = eval(f.read())
    for cookie in cookies:
        driver.add_cookie(cookie)
    print(f'cookies loaded of {cookies_name}')

#this function to make the login process and saves the cookies for further login 
def login_to_twitter(email,password):
        cookies_name=f'{email.replace('@','_')}.txt'
        chrome_options3 = Options()
        chrome_options3.add_argument("--disable-notifications")
        driver4 = webdriver.Chrome(options=chrome_options3)
        login = "https://twitter.com/i/flow/login"
        driver4.get(login)
        username_input = WebDriverWait(driver4, 20).until(
            EC.presence_of_element_located((By.NAME, "text")))
        if username_input:
            time.sleep(2)
            username_input.send_keys(email)
        time.sleep(2)
        click_next = WebDriverWait(driver4, 20).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Next')]")))
        click_next.click()
        password_input = WebDriverWait(driver4, 20).until(
            EC.presence_of_element_located((By.NAME, "password")))
        if password_input:
            time.sleep(2)
            password_input.send_keys(password)
        time.sleep(1)
        login_button = WebDriverWait(driver4, 20).until(
            EC.presence_of_element_located((
                By.XPATH, "//span[contains(text(),'Log in')]")))
        login_button.click()
        time.sleep(10)
        cookies = driver4.get_cookies()
        with open(f"cookies/{cookies_name}", "w", encoding="utf-8") as f:
            f.write(str(cookies))
        print('we got the cookies')
        driver4.quit()

# compares the time post made in in the current time 
def compare(given_time_str):
    given_time = datetime.strptime(given_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    current_time = datetime.now()
    current_time -= timedelta(hours=3)
    time_difference = current_time - given_time
    confirmation=False
    if time_difference <= timedelta(minutes=15):
        confirmation=True
    else:
        pass
    return confirmation,time_difference

# to make sure no emoji is entered in the user name
def is_bmp(character):
        return ord(character) <= 0xFFFF

# to make humainated typing
def human_like_typing(text, input_field):
     lines = text.split('\n')
     for line in lines:
        filtered_text = ''.join(char for char in line if is_bmp(char))
        for char in filtered_text:
            input_field.send_keys(char)
            time.sleep(0.1)

# to get the tweets we need to scrape
def scrape_text_with_dollar_sign(driver, link):
    username=link.replace("https://twitter.com/","")
    search_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "(//div[@class='css-175oi2r r-sdzlij r-dnmrzs r-1awozwy r-18u37iz r-1777fci r-xyw6el r-o7ynqc r-6416eg'])[2]")))
    try:
        time.sleep(3)
        print(f'searching for user : {username}')
        search_button.click()
    except:
        print('try again click search')
        driver.refresh()
        search_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '(//*[name()="svg"][@class="r-4qtqp9 r-yyyyoo r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-18jsvk2 r-lwhw9o r-cnnz9e"])[2]')))
        if search_button:
            time.sleep(3)
            search_button.click()
    input_field=WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search query"]')))
    if input_field:
        time.sleep(1)
        human_like_typing(username,input_field)
    choose_user_name=WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, f'(//span[@class="css-1qaijid r-bcqeeo r-qvutc0 r-poiln3" and text()="@{username}"])[1]')))
    if choose_user_name:
      time.sleep(2)
      choose_user_name.click()

    tweets = WebDriverWait(driver,30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
    driver.execute_script("window.scrollBy(0, 1000);")
    tweets = WebDriverWait(driver,30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
    tweets_data=[]      
    for tweet in tweets:
        try:
         timestamp_element = WebDriverWait(tweet,5).until(EC.presence_of_element_located((By.XPATH, './/time'))).get_attribute('datetime')
         confirmation,time_difference =compare(timestamp_element)
         if confirmation:
            tweets_data.append(tweet)
            tweet_text = WebDriverWait(tweet,5).until(EC.presence_of_element_located((By.XPATH, './/div[@data-testid="tweetText"]'))).text
            matches = re.findall(r'\$([A-Za-z_]+)', tweet_text)
            
            count_dict = {}
            for match in matches:
                count_dict[match] = count_dict.get(match, 0) + 1
            
            if count_dict:
                print(f'In last {time_difference} mins for account {link.replace("https://twitter.com/","")}\n')  # Print the account name
                for match, count in count_dict.items():
                    print(f"{match} : {count} time{'s' if count != 1 else ''}")  
            else:
                print("No Stock found in the tweet.")
        except:
            pass
    if not tweets_data:
        print("There are no new posts in the last 15 minutes")       

# the main process
url = "https://twitter.com/"
chrome_options1 = Options()
chrome_options1.add_argument("--disable-notifications")
chrome_options1.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=chrome_options1)
driver.get(url)
file_name = f"{email.replace('@', '_')}.txt"
file_path = os.path.join("cookies", file_name)
if not os.path.exists(file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("[]")
time.sleep(3)
load_cookies(driver, file_name)
time.sleep(1)
driver.get(url)
make_sure_we_loged_in = ''
try:
    make_sure_we_loged_in = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '(//*[name()="svg"][@class="r-4qtqp9 r-yyyyoo r-dnmrzs r-bnwqim r-1plcrui r-lrvibr r-18jsvk2 r-lwhw9o r-cnnz9e"])[1]')))
    if make_sure_we_loged_in:
        print('we already loged in before')
except Exception as e:
    print("we need to login")
    login_to_twitter(email,password)
if not make_sure_we_loged_in:
    time.sleep(3)
    load_cookies(driver, file_name)
    time.sleep(1)
    driver.refresh()

# List of Twitter profile links
links = [
    'https://twitter.com/Mr_Derivatives',
    'https://twitter.com/warrior_0719',
    'https://twitter.com/ChartingProdigy',
    'https://twitter.com/allstarcharts',
    'https://twitter.com/yuriymatso',
    'https://twitter.com/TriggerTrades',
    'https://twitter.com/AdamMancini4',
    'https://twitter.com/CordovaTrades',
    'https://twitter.com/Barchart',
    'https://twitter.com/RoyLMattox',
]

# Loop through each link and scrape text with dollar signs in recent tweets
while True :
 for link in links:
    scrape_text_with_dollar_sign(driver, link)
 print('sleeping for 15 minutes')
 time.sleep(15*60)

driver.quit()