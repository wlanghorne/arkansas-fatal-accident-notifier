from datetime import datetime 
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import json
import os
import shutil
import base64
from time import sleep

# Get the number of the last recorded fatal 
def get_old_fatal(path):
    if not os.path.exists(path):
        with open(path, 'w') as f: 
            f.close()
        return None
    else: 
        old_fatal_num = ''
        with open(path, 'r') as f:
            old_fatal_num = f.readline()
            f.close()
        return old_fatal_num

# Open the latest year lists on the ADP website with fatals listed 
def open_fatal_log(driver, url):
    # Update status in terminal
    print("Opening url ...")

    driver.get(url)

    # Delay to allow data to load 
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'contentArea')))

    content_area = driver.find_element(By.CLASS_NAME, 'contentArea')
    content_links = content_area.find_elements(By.TAG_NAME, 'a')

    # Open first link (lastest year)
    content_links[0].click()

    # Delay to allow data to load 
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.LINK_TEXT, 'Back To Summary Years')))

# Get the number of the latest fatal car accident listed on the site 
def get_latest_fatal(driver):
    # Nagivate to content links
    content_area = driver.find_element(By.CLASS_NAME, 'contentArea')
    content_links = content_area.find_elements(By.TAG_NAME, 'a')

    # Get the text and link from the second link (lastest entry)
    latest_fatal_link = content_links[1]
    latest_fatal_text = latest_fatal_link.get_attribute('innerHTML')
    
    # Get the number of the latest fatal wreck 
    latest_fatal_num = latest_fatal_text.split(' ')[0]

    return latest_fatal_num, latest_fatal_link

# Determine whether to update based on the values of last processed fatal and the latest reported fatal 
def to_update_fatals(old_fatal_num, latest_fatal_num, driver):
    if not old_fatal_num or old_fatal_num != latest_fatal_num:
        # No fatals have been processed or the last fatal is out of date
        print("Updating fatals")
    else: 
    	print("No fatals to update")
    	driver.quit()
    	exit()

# Write latest fatal to last fatal file
def write_latest_fatal(latest_fatal_num, old_fatal_path):
    with open(old_fatal_path, 'w') as f: 
        f.write(latest_fatal_num)
        f.close()

# get a victim's role (driver, passenger, pedestrian) in a crash 
def get_victim_role(cells):
    counter = 0
    for cell in cells: 
        if 'X' in cell.get_attribute('innerHTML'):
            if counter == 0:
                return 'driver'
            elif counter == 1: 
                return 'passenger'
            else:
                return 'pedestrian'

# get data from victim (deceased or injured) tables
def get_victim_tables(rows):
    victim_dict = {}
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')

        # Get the deceased person's name
        deceased_cell = cells[0].get_attribute('innerHTML').strip()
        deceased_name = deceased_cell.split('(')[0]
        deceased_vehicle_num = ''.join(n for n in deceased_cell.split('(')[1][:-1] if n.isdigit())

        # Get deceased person's age
        deceased_age = cells[1].get_attribute('innerHTML').split('&nbsp')[0].strip()

        # Get deceased person's city of residence 
        city_of_res = cells[2].get_attribute('innerHTML').split('&nbsp')[0].strip()

        # Get deceased person's sex 
        sex = cells[3].get_attribute('innerHTML').split('&nbsp')[0].strip()

        role = get_victim_role(cells[4:6])

        # Put data into dictionary 
        victim_dict[deceased_name] = {'vehicle_num': deceased_vehicle_num, 'age': deceased_age, 'city_of_res': city_of_res, 'sex': sex, 'role': role}

    return victim_dict

# Get additional victim data stored for some reason in a different format in tables seperate from the other victim tables
def get_additional_victims(row):

    # Try to get cell within row. If there is no cell, there is no additional data to write 
    try:
        cell = row.find_element(By.CSS_SELECTOR, 'td')
    except: 
        return False
    else: 
        data = cell.get_attribute('innerHTML').strip().split(':')[:-1]
        data_lists = []

        victim_num = len(data)/7
        
        for i in victim_num:
            start  


        return {'person': 'data'}



# Open link to and get information on the latest fatal accident 
def get_latest_data(driver, latest_fatal_num, latest_fatal_link):

    # FOR TESTING PURPOSES ONLY. UNCOMMENT CLICK CODE BELOW WHEN DONE
    driver.get(latest_fatal_link)

    # Open the latest fatal link 
    #latest_fatal_link.click()

    # Create a dictionary to store data from the latest fatal
    fatal_data = {'fatal_num': latest_fatal_num}

    # Nagivate to content links
    content_area = driver.find_element(By.CLASS_NAME, 'contentArea')
    wrapper_table = content_area.find_element(By.CSS_SELECTOR, 'table')
    content_tables = wrapper_table.find_elements(By.CSS_SELECTOR, 'table')

    # Pull data from second content table
    cells = content_tables[1].find_elements(By.CSS_SELECTOR, 'td')
   
    # Get the accident number
    raw_accident_num = cells[0].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    accident_num = raw_accident_num.split('&nbsp')[0]
    fatal_data['accident_num'] = accident_num

    # Get the number deceased
    raw_deceased_num = cells[2].get_attribute('innerHTML')
    deceased_num = ''.join(n for n in raw_deceased_num if n.isdigit())
    fatal_data['deceased_num'] = deceased_num

    # Get the number injured
    raw_injured_num = cells[3].get_attribute('innerHTML')
    injured_num  = ''.join(n for n in raw_injured_num if n.isdigit())
    fatal_data['injured_num'] = injured_num

    # Pull data from third content table
    cells = content_tables[2].find_elements(By.CSS_SELECTOR, 'td')

    # Get the date 
    raw_date = cells[0].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    date = raw_date.split('&nbsp')[0]
    fatal_data['date'] = date

    # Get the time
    raw_time = cells[1].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    time = raw_time.split('&nbsp')[0]
    fatal_data['time'] = time

    # Get the location 
    raw_location = cells[2].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    location = raw_location.split('&nbsp')[0]
    fatal_data['location'] = location

    # Get the city 
    raw_city = cells[3].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    city = raw_city.split('&nbsp')[0]
    fatal_data['city'] = city

    # Get the county 
    raw_county = cells[4].find_element(By.CSS_SELECTOR, 'u').get_attribute('innerHTML')
    county = raw_county.split('&nbsp')[0]
    fatal_data['county'] = county

    # Pull data from fourth content table (data on those who died in accident)
    rows = content_tables[3].find_elements(By.CSS_SELECTOR, 'tr')

    # Get deceased data 
    fatal_data['deceased'] = get_victim_tables(rows[1:-1])

    # Pull data from fifth content table (additional data on those who died in accident)
    rows = content_tables[4].find_elements(By.CSS_SELECTOR, 'tr')
    add_deceased = get_additional_victims(rows[1])

    if add_deceased: 
        fatal_data['deceased'].update(add_deceased)

    # Pull data from sixth content table (data on those injured in accident)
    rows = content_tables[5].find_elements(By.CSS_SELECTOR, 'tr')

    # Get injured data 
    fatal_data['injured'] = get_victim_tables(rows[1:-1])

    # Pull data from seventh content table 
    rows = content_tables[6].find_elements(By.CSS_SELECTOR, 'tr')
    add_injuried = get_additional_victims(rows[1])

    if add_injuried:
        fatal_data['injured'].update(add_injuried)

    # Pull data from eighth content table 
    rows = content_tables[7].find_elements(By.CSS_SELECTOR, 'tr')

    print(fatal_data)




