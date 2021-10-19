# SERP google crawler
# Make a crawler that checks the google ranking position of certain websites
# under certain keywords. Load it onto a droplet and automate it so that it
# updates itself on a weekly basis and shows the results on a webpage, set up
# specifically for this.
#
# The idea is to create an initial request, out of which to scrap nine further
# search result pages and add them to a list in which the initial request is
# appended in the beginning. It then loops through the list, performing a
# request on each element and scraping the request for the URLs of search
# results, collecting them in a list. Finally, it looks through this list and
# searches for target substring in element. Upon finding it, a dictionary
# element is created containing the found URL, Index position inside list as
# well as the date this element was created. It is then appended to the lists
# of current_position and historic_position.
#
# Test run -------------------------------------------------------------------
# Successful!
# Target : fotofabrik
# Terms : fotobuch erstellen
#
# Result :
# [{'URL': 'https://www.fotofabrik.de/fotobuch-erstellen/',
# 'Position': 23,
# 'Date': '2020-09-24T00:01:55.345727'}]
#
#-----------------------------------------------------------------------------
# Script start----------------------------------------------------------------

# Dependencies
import sys
import re
import csv
import urllib
import requests
import os
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from datetime import datetime

# Functions
# Sanitize input
#def sanitize(term):
def sanitize(term):
	cleanterm = re.sub('\W+',' ', term)
	return cleanterm

# Uses sanitized terms to create 10 URL's to visit
def create_urls(cleanterm):
	query_url_list = []
	page = 0
	urlterm = cleanterm.replace(' ', '+')
	while page < 91:
		query = 'https://www.google.com/search?q={}&sxsrf=ACYBGNTx2Ew_5d5HsCvjwDoo5SC4U6JBVg:1574261023484&ei=H1HVXf-fHfiU1fAP65K6uAU&start={}&sa=N&ved=0ahUKEwi_q9qog_nlAhV4ShUIHWuJDlcQ8tMDCF8&biw=1280&bih=561&dpr=1.5'.format(urlterm,page)
		query_url_list.append(query)
		page+=10
	query_url = query_url_list[0]
	return query_url_list

# Creates requests using sanitized input
def create_request(query_url):
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
	headers = {"user-agent" : USER_AGENT,
		"Host" : "www.google.com",
		"Referer" : "https://www.google.com/"
	}
	resp = requests.get(query_url, headers=headers)
	return resp

# Looks at response given to requests and checks for http error
def check_status(resp):
	if resp.status_code != 200:
		print("HTTP Status not 200")
		exit()
	else:
		soup = BeautifulSoup(resp.content, "html.parser")
		viewsoup = soup.prettify()
	return soup

# Removes adjacent duplicates in list
def remove_dup(x):
	scraping_final = []
	a = x[:1]
	for item in x[1:]:
		if item != x[-1]:
			scraping_final.append(item)
	return scraping_final

# Creates directory using the input as directoryname
def create_dir(cleanterm):
	dirterm = cleanterm.replace(' ', '')
	dirpath = "/home/mclovin/Documents/ScrapCrawl/scrapresults/{}".format(dirterm)
	try:
		os.mkdir(dirpath)
	except OSError:
		pass
#		print("Creation of directory failed")
	else:
		print("Successfully created directory")
	return dirpath

# Scrapes the search result's URL's into a list
def collect_results(soup):
	global scrape_results
	scraping = []
	scraping = list(map(str, soup.find_all("div", class_= "yuRUbf")))
#	print(scraping)
	scraping_one = [i.split('href="', 1)[1] for i in scraping]
	scraping_two = [i.split('" onmousedown', 1)[0] for i in scraping_one]
#	print(scraping_two)
	scraping_final = remove_dup(scraping_two)
#	print(scraping_final)
	for i in scraping_final:
		scrape_results.append(i)
	for i in scraping_final:
		scrapindex = str(scraping_two.index(i))
#		print(scrapindex + i + ", /n")

#for i in scraping_final:
#    scrap_position = scraping_final.index(i)
#    item = {
#        "Position": scrap_position,
#        "URL": i
#        }
#    name_of_file.append(item)
	return scrape_results

#------------------------------------------------------------------------------
# UNFINISHED
# export query results list as csv
def record_results_csv():
	filename1 = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	sys.stdout = open(filename1 + '.csv', 'w')
# define csv headers

# append current position to csv collecting historical data
def create_historical_csv(cleanterm, dirpath):
	cleanterm = sanitize(term)
	dirpath = create_dir(cleanterm)
	myfile = csv.open("{}.csv".format(cleanterm))
	fpath = (dirpath / "{}".format(cleanterm)).with_suffix('.csv')
#    with fpath.open(mode='w+') as csvfile:
#         add csv write code
# UNFINISHED
#------------------------------------------------------------------------------

# Checks position of target in scrape results.
def check_position(scrape_results):
	current_position = []
	scrape_results = collect_results(soup)
	curr_time = datetime.now()
	if any(target in s for s in scrape_results) == True:
		found_url = [x for x in scrape_results if re.search(target, x)]
		search_position = scrape_results.index(found_url[0])
		item = {
			"URL": found_url[0],
			"Position": search_position,
			"Date": curr_time.isoformat()
			}
		current_position.append(item)
	else:
		item = {
			"URL": "URL not found",
			"Position": ">100",
			"Date": curr_time.isoformat()
			}
		current_position.append(item)
	return current_position


term = "fotobuch erstellen"
target = "fotofabrik"
scrape_results = []
counter = 0

# Final scraper
cleanterm = sanitize(term)
create_dir(cleanterm)
query_url_list = create_urls(cleanterm)
for query_url in query_url_list:
	resp = create_request(query_url)
	soup = check_status(resp)
	collect_results(soup)
#	sleep(randint(5,30))
current_position = check_position(scrape_results)
print(current_position)
