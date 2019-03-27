# Beginning Date: 7/31/18 1:15PM

import requests
import bs4
import os

num_chapters = 439
save_path = ''

for i in range(num_chapters):

	current_chapter = i + 1

	# Get chapter page source from Wuxia World
	response = requests.get('https://www.wuxiaworld.com/novel/*%s' % current_chapter )
	
	# Used Beautiful Soup to easily extract chapter from the html 
	soup = bs4.BeautifulSoup(response.text)
	chapter = soup.select('.fr-view p')
	chapter_title = chapter[0].text

	# Save the chapter to a txt file
	filename = chapter_title + '.txt'
	absolute_path = os.path.join(save_path, filename)

	for para in chapter:
		with open(absolute_path,'a+') as f:
			f.writelines(para.text)
			f.writelines('\n')
			f.writelines('')
			f.writelines('\n')

break
