# Beginning  Date: 7/31/18 1:15PM
# Completion Date: 7/31/18 1:50PM

# Program Version: 1.0.0

import bs4, sys, os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from logger import setup_custom_logger

exit_message = 'Thank you for using Wuxia Novelscraper!'

# Function that downloads the chapters
def requests_session(url):
	''' Tries downloading the page 5 times before giving up '''
	requests_session = requests.Session()
	requests_retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ]) # Forces it to retry and ignore common HTTP errors
	requests_session.mount('http://', HTTPAdapter(max_retries=requests_retries))
	response = requests_session.get(url, headers={'User-agent':bot_name})

	return response

# Removes invalid filename characters
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


''' Start of the program '''
app_version = '1.0.0'
logger = setup_custom_logger(app_version)
bot_name = ('Wuwuro Bot %s' %app_version)

''' These are the changeable variables '''
save_path = '' # * MUST create a folder with the novel name
novel_url = '' # * MUST copy the whole URL here. EXCEPT the chapter number
start_at_chap = 0 # * MUST change this based on where you want to start
end_at_chap = 0 # * MUST change this based on where you want to END
''' These are the changeable variables '''

''' Starting the scraper '''
for current_chapter in range(start_at_chap, end_at_chap + 1):
	
	chapter_url = novel_url + str(current_chapter)

	''' Download the page source, Get the chapter, Log errors '''
	print('Downloading Chapter-%s (%s)' % (current_chapter, chapter_url))
	try:
		response = requests_session(chapter_url)
	except Exception as e:
		logger.info('Failed to download %s' % chapter_url, exc_info=True)
		continue

	''' Parsing the HTML File '''
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	chapter = soup.select('.fr-view p')
	chapter_title = chapter[1].text
	print('Downloaded %s' % chapter_title)


	''' Saving it to a text file '''
	filename = chapter_title + '.txt'
	filename = remove_invalid_char(filename)
	absolute_path = os.path.join(save_path, filename)
	
	try:
		# For paragraph in chapter
		for para in chapter:
			with open(absolute_path,'a+') as f:
				f.writelines(para.text)
				# Retain the previous format. Empty line after each paragraph
				f.writelines('\n')
				f.writelines('')
				f.writelines('\n')
	except Exception as e:
		logger.error('Failed to save to %s' % filename, exc_info=True)

	print("Saved to '%s' " % filename)
	print()

print(exit_message)
