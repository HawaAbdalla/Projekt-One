# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 06:52:01 2024

@author: PC
"""

#%%
"""
Website specific program to scroll until certain condition is met and gather links and dates for appropriate items.

Program scrolls on webpage and clicks load more button until a certain break condition is met (i.e. when '2013' is found in date element).

When this break condition is met, the program scrolls to the top of the webpage while appending certain links and dates to a list.  
The links and dates are then written to a .txt file.

"""
# Import relevant module items for scrolling on dynamically loaded webpages
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# Update path to ChromeDriver
path='r/Users/hawaabdalla/Desktop/chromedriver-mac-arm64/chromedriver'

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# Initialize driver and maximize window
driver.get('https://www.rev.com/transcripts?')
driver.maximize_window()
time.sleep(5)

# Close pop-up windows
CookiesPopup = driver.find_element(By.ID, "hs-eu-close-button")
CookiesPopup.click()
time.sleep(2)

UpdatePopup = driver.find_element(By.ID, "pendo-close-guide-56bbd323")
UpdatePopup.click()
time.sleep(2)


links_trump=[]   # Initialize empty list to store links to speeches and dates

proceed=True   # Variable to control scrolling and loading more of webpage   


while proceed == True:   
    try:   # While 'proceed' is True, try following:
        driver.execute_script('window.scrollBy(0,600);')   # Scroll down page by 600 pixels
        time.sleep(1)
        load_more = driver.find_element(By.XPATH, '/html/body/div/main/section[1]/div/div/div/div[2]/div/div[2]/a[2]/div')   # Find 'load more' button by XPATH
        load_more.click()   # Click 'load more'
        time.sleep(1)
        
        years=driver.find_elements(By.XPATH, ".//div[contains(@class, 'blog-article-card_meta')]")   # Find date elements by XPATH
        
        for year in years:   # Loop over the date elements
            if "2013" in year.text:   # Set condition to stop if '2013' is found in date
                proceed = False   # If condition is met, set variable 'proceed' to False
                
        if proceed == False:   # If proceed == False, execute following block of code
            time.sleep(3)
            driver.execute_script('window.scrollTo(0,0);')   # Scroll to top of page
            time.sleep(3)
            links = driver.find_elements(By.XPATH,'//a[contains(@href, "trump")]')   # Find links by XPATH containing 'trump'
            for link in links:   # Loop over links
                href = link.get_attribute('href')   # Get href attribute associated with link
                try:
                    if 'rally' in href or 'speech' in href:   # Find links with keywords 'rally' or 'speech'
                        date_element = link.find_element(By.XPATH, ".//div[contains(@class, 'blog-article-card_meta')]")   # Find the related date element by XPATH
                        date = date_element.text   # Convert date element to text
                        links_trump.append((date,href))   # Append date and link to list
                except NoSuchElementException:   # Set except condition for missing date
                    print(f'Link: {href} - Date: Not found')   # Print error message if date not found
                
       
    except (NoSuchElementException, ElementClickInterceptedException):   # Set except condition if loading page failed
        print("Error loading more")   # Print error message if failed
        break 

driver.quit()   # Quit driver
    
# Open file in writing mode
with open('links_trump.txt','w') as file:
    for date,link in links_trump:   # Loop over date, link pairs in list  
        file.write(f'{date}\n{link}\n\n')   # Write date and link to file

