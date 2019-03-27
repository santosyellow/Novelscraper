# Beginning  Date: 8/1/18 12:05AM
# Completion Date: 8/1/18 12:40AM

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from logger import setup_custom_logger
import requests
import bs4
import sys
import os


exit_message = 'Thank you for using Wuxia Novelscraper!'


def requests_session(url):
	''' Try downloading the page 5 times before giving up '''
	requests_session = requests.Session()
	requests_retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
	requests_session.mount('http://', HTTPAdapter(max_retries=requests_retries))
	response = requests_session.get(url, headers={'User-agent':bot_name})

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


''' Start of the program '''
app_version = '1.2.0'
logger = setup_custom_logger(app_version)
bot_name = ('Wuwuro Bot %s' %app_version)

print('%s:' % bot_name)



''' These are the changeable variables '''
save_path = '' # * MUST create a folder with the novel name
novel_url = '' # * MUST copy the whole URL here. EXCEPT the chapter number
backup_url = ''
start_at_chap = 0 # * MUST change this based on where you want to start
end_at_chap = 0 # * MUST change this based on where you want to END
''' These are the changeable variables '''



for current_chapter in range(start_at_chap, end_at_chap + 1):
	''' Starting the scraper '''
	chapter_url = novel_url + str(current_chapter)
	backup_chapter_url = '%s' % current_chapter #backup_url + str(current_chapter)

	''' Download the page source, Get the chapter, Log errors '''
	print('Downloading Chapter-%s (%s)' % (current_chapter, chapter_url))
	response = requests_session(chapter_url)
	if response.status_code != 200:
		logger.error('Failed to download %s' % chapter_url)
		print('Trying backup URL...')
		response = requests_session(backup_chapter_url)
	if response.status_code != 200:
		logger.error('Backup URL Failed', exc_info=True)
		sys.exit()

	''' Parsing the HTML File '''
	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	chapter = soup.select('.fr-view p')
	chapter_title = soup.select('.caption.clearfix h4')[0].text
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
				# Retain the previous format. Empty line after each para.
				f.writelines('\n')
				f.writelines('')
				f.writelines('\n')
	except Exception as e:
		logger.error('Failed to save to %s' % filename, exc_info=True)

	print("Saved to '%s' " % filename)
	print()

print(exit_message)
sys.exit()
