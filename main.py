# -*- coding: utf-8 -*-

# Encoding above makes it backwards compatible for Python 2

# Beginning  Date: 3/26/19 3:25PM
# Completion Date: 3/26/19 4:00PM

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from logger import setup_custom_logger
import requests
import bs4
import sys
import os

exit_message = 'Thank you for using Wuxia Novelscraper, Come again!'

# Function that downloads the chapters
def requests_session(url):
	''' Tries downloading the page 5 times before giving up '''
	requests_session = requests.Session()
	requests_retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	requests_session.mount('http://', HTTPAdapter(max_retries=requests_retries))
	proxies = {
		'http': '149.56.46.36:8080',
		'https': '198.27.67.35:3128'
	} # Proxies from free-proxy.cz (They may reset connection after several downloads...)

	response = requests_session.get(url, headers={'User-agent':bot_name}, proxies=proxies)

	return response

def find_title(chapter):
	# Printable characters except for spaces, tabs, and newlines
	not_spaces = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '\x0b', '\x0c']
	
	for line in chapter:
		for char in line.text:
			if char in not_spaces:
				return line.text

def remove_invalid_char(string):
	for char in string:	
		# Spare those who can be spared
		if char == '?':
			return string.replace('?','')
		elif char == '"':
			return string.replace('"',"'")
		elif char == ':':
			return string.replace(':','-')
		# If not, replace them with underscores. It can't be helped
		for invalid in '" * / : < > ? \\ |'.split():
			string = string.replace(invalid,'_')
		return string

def process_text(filename):
    open(filename,'a+') # this line makes sure the file exists; if it doesn't, it creates the file.
    with open(filename,'r') as f:
        raw_data = f.readlines()

    # The list that readlines() provides contains newline characters: '\n'
    # Wuwuro doesn't view a string with a newline and a string without AS the same
    # So we have to remove the newline characters for every item in the list
    processed_data = []
    for i in range(len(raw_data)):
        processed_data.append(raw_data[i].replace('\n', ''))
    return processed_data


''' Start of the program '''
app_version = '2.0.0'
logger = setup_custom_logger(app_version)
bot_name = ('Wuwuro Bot %s' %app_version) # This will appear as our User-Agent

print(bot_name + '\n')



''' These are the changeable variables '''
save_path = '' # !!!MUST create a folder with the novel name
novel_url = '' # !!!MUST copy the whole URL here. EXCEPT the chapter number
backup_url = '' # Sometimes the URL changes format so it's important to have the backup URL
start_at_chap = 0 # * Change this based on where you want to start
end_at_chap = 0 # * Change this based on where you want to END

''' END of changeable variables '''



for current_chapter in range(start_at_chap, end_at_chap + 1):

	''' Starting the scraper '''
	chapter_url = novel_url + str(current_chapter) # Join provided novel url and current chapter number to get the current chapter URL
	backup_chapter_url = backup_url + str(current_chapter) # Same as above but using the backup URL

	''' Download the page source, Get the chapter, Log errors '''
	''' Check if downloaded before '''
	downloaded_chapters = process_text('downloaded_chapters.txt')

	# Checking if the chapter wasn't downloaded yet; if not, download the chapter
	if (chapter_url not in downloaded_chapters and backup_chapter_url not in downloaded_chapters):

		print('Downloading Chapter-%s (%s)' % (current_chapter, chapter_url))
		response = requests_session(chapter_url)
		main_url = True

		# If the chapter_url didn't work
		if response.status_code != 200:
			
			logger.error('Failed to download %s' % chapter_url)
			print('Trying backup URL...')
			response = requests_session(backup_chapter_url)

			# If the backup URL also didn't work
			if response.status_code != 200:
				logger.error('Backup URL also failed', exc_info=True)
				sys.exit() # Quit the program

			main_url = False

	else:
		if chapter_url in downloaded_chapters:
			print('%s was already downloaded before.' % chapter_url)
		elif backup_chapter_url in downloaded_chapters:
			print('%s was already downloaded before.' % backup_chapter_url)
		print()
		continue


	''' Parsing/Processing the HTML File '''
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	chapter = soup.select('.fr-view p') # A list data type. stores each paragraph in separate sections.
	chapter_title = soup.select('.caption.clearfix h4')[0].text
	print('Downloaded %s' % chapter_title)

	''' Saving the chapter to a text file '''
	filename = chapter_title + '.txt'
	filename = remove_invalid_char(filename)
	absolute_path = os.path.join(save_path, filename)
	
	try:
		# For paragraph in chapter
		for para in chapter:
			with open(absolute_path,'a+') as f:
				f.writelines(para.text.encode('utf-8')) # Throws out error because the string is Unicode
				# Retain the previous format. Empty line after each para.
				f.writelines('\n')
				f.writelines('')
				f.writelines('\n')
	except Exception as e:
		logger.error('Failed to save to %s' % filename, exc_info=True)

	print("Saved to '%s' " % filename)
	
	''' Add the correct URL to downloaded_chapters.txt'''
	with open('downloaded_chapters.txt','a+') as f:
		try:
			# If chapter_url worked
			if main_url:
				f.writelines(chapter_url)
				f.writelines('\n')
			# If chapter_url didn't work but backup_url worked
			else:
				f.writelines(backup_chapter_url)
				f.writelines('\n')
			print('Saved to downloaded chapters')
			
		except:
			logger.error('Failed to write URL to downloaded_chapters.txt', exc_info=True)
	print()

print(exit_message)
sys.exit()
