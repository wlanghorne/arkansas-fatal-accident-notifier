from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from scraper_functions import get_old_fatal, open_fatal_log, get_latest_fatal, to_update_fatals, write_latest_fatal, get_latest_data
from writer_functions import gen_msg
from time import sleep
from datetime import date
import csv
import os
import sys 

# Paths to csv file that will store data 
output_path = './outputs'
old_fatal_path = os.path.join(output_path, 'old_fatal.txt')
driver_path = './chromedriver'
url = 'https://www.ark.org/asp-fatal/index.php'

# Process args 
argv = sys.argv
argv_len = len(argv)
if argv_len < 4:
	print('ERROR: Must enter at least three arguments. 1) sender email address, 2) path to file with Google API JSONs, 3-n) recipient email addresses')
	exit()
else: 
	SENDER_ADDRESS = argv[1]
	PATH_TO_API_FILES = argv[2]
	RECIP_ADDRESSES = []
	for i in range (3, argv_len):
		RECIP_ADDRESSES.append(argv[i])

# Get the number of the last fatal car accident processed 
old_fatal_num = get_old_fatal(old_fatal_path)

# Initiate driver
chrome_options = Options()
chrome_options.add_argument("--headless")
s = Service(driver_path)
driver = webdriver.Chrome(service=s, options=chrome_options)

# Open latest year
open_fatal_log(driver, url)

# Get the number of the latest fatal car accident
latest_fatal_num, latest_fatal_link = get_latest_fatal(driver)

# LINK CHANGE FOR TESTING PURPOSES 
latest_fatal_link = 'https://www.ark.org/asp-fatal/index.php?do=view_reports&accident_number=175&year_rec=2022'

# Compare the last fatal to the latest fatal. Program with exit if updating is not required
to_update_fatals(old_fatal_num, latest_fatal_num, driver)

# Write latest fatal to last fatal file
write_latest_fatal(latest_fatal_num, old_fatal_path)

# Open latest fatal file and get info
fatal_dict = get_latest_data(driver, latest_fatal_num, latest_fatal_link)

# Take all the info for the latest fatal file and process it into a message that can sent via email
gen_msg(fatal_dict, driver)

# Quit driver 
driver.quit()