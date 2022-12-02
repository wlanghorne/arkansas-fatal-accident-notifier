from scraper_functions import scrape_page
from writer_functions import gen_msg
from email_functions import gen_email
from time import sleep
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
	sender_address = argv[1]
	path_to_api_files = argv[2]
	recip_addresses = []
	for i in range (3, argv_len):
		recip_addresses.append(argv[i])

# Scrape page and return a dictionary with 
fatal_dict, report_url = scrape_page (driver_path, url, old_fatal_path)

# Take all the info for the latest fatal file and process it into a message that can sent via email
body = gen_msg(fatal_dict, report_url)

# Generate and send email 
gen_email(body, recip_addresses, sender_address, path_to_api_files)