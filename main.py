## This code for this time being only gather the user profiles out from behance.net
## It gather data from the first page of the search result and then scroll down to the end of the page
## After this the Name, Company, Profile pic, link of the profile are collected and written to a csv file

import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## Used for scrolling down the page
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    

## Automatic google sign in if you added email and password for more results
def sign_in_with_google(driver, email, password):
    sign_in_button = driver.find_element(By.ID, 'google-sign-in-button')
    sign_in_button.click()
    driver.switch_to.window(driver.window_handles[-1])
    email_input = driver.find_element(By.ID, 'identifierId')
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    password_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, 'password'))
    )
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    driver.switch_to.window(driver.window_handles[0])

## Profile info scrapper
def scrape_profile_info(driver, writer,profile_link):
    driver.switch_to.window(driver.window_handles[-1])
    profile_pic = driver.find_element(By.XPATH, '//img[contains(@class, "AvatarImage-avatarImage-PUL")][1]').get_attribute('src')
    name = driver.find_element(By.CLASS_NAME, 'ProfileCard-userFullName-ule').text
    company = driver.find_element(By.CLASS_NAME, 'ProfileCard-line-fVO').text
    
    writer.writerow([name, company,profile_pic,profile_link])

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

## counting total profiles scrapped along with writing data to csv
def count_users(url, class_name, email, password):
    # Specify the path to the chromedriver executable
    service = Service(executable_path="driver\chromedriver\chromedriver.exe")

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Initialize the Chrome WebDriver with the specified service and options
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)


    if email and password:
        if 'Sign in with Google' in driver.page_source:
            sign_in_with_google(driver, email, password)

    prev_count = 0
    current_count = len(driver.find_elements(By.CLASS_NAME, class_name))

    while prev_count != current_count:
        prev_count = current_count
        scroll_to_bottom(driver)
        current_count = len(driver.find_elements(By.CLASS_NAME, class_name))

    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Company', 'Profile pic', 'link'])

        user_divs = driver.find_elements(By.CLASS_NAME, class_name)
        for user_div in user_divs:
            profile_link_element = user_div.find_element(By.TAG_NAME, 'a')
            profile_link = profile_link_element.get_attribute('href')

            driver.execute_script("window.open(arguments[0], '_blank');", profile_link)

            scrape_profile_info(driver, writer,profile_link)

    total_users = current_count

    driver.quit()

    return total_users

## Add the country name you want to scrape data (i.e, United Kingdom, Pakistan etc)
country = input("Enter the country name: ")
cntry = re.sub("\s+", "+", country.strip())

url = f'https://www.behance.net/search/users?tracking_source=typeahead_search_direct&country={cntry}'
class_name = 'UserSummary-ownerLinkWrap-OlV'

email = input("Enter your email (you can leave it empty if you don't want to sign in): ")
password = input("Enter your password (you can leave it empty if you don't want to sign in): ")

total_users = count_users(url, class_name, email, password)
print(f'Total number of users: {total_users}')
