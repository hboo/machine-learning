from lxml import html
from bs4 import BeautifulSoup
import requests
import json

def parse_top_reviewers():
	page = requests.get('https://www.beeradvocate.com/members/?sort=beers')
	tree = html.fromstring(page.content)
	user_urls = []
	for i in xrange(3, 1000, 4):
		xpath = '//*[@id="ba-content"]/div[{}]/a/@href'.format(i)
		user_urls.append(tree.xpath(xpath)[0])
	return user_urls

def parse_reviews(user):
	#split the user href that looks like '/community/members/jmdrpi.276070'
	username = user.split('/')[3].split('.')[0]
	index = 0
	reviews = []
	while True:
		user_reviews_url = 'https://www.beeradvocate.com/user/beers/?start={index}&ba={user}&order=dateD&view=R'.format(index=str(index), user=username)
		page = requests.get(user_reviews_url)
		soup = BeautifulSoup(page.text, 'lxml')
		tbl = soup.find_all('table')
		rows = tbl[0].find_all('tr')[3:]
		
		if len(rows) < 1:
			return reviews

		for row in rows:
			data = row.find_all('td')
			name = data[2].find_all('a')[0].text
			brewery = data[2].find_all('a')[1].text
			style = data[2].find_all('a')[2].text
			abv = data[3].text
			rating = data[4].text
			r_dev = data[5].text

			reviews.append({
					'name' : name,
					'brewery' : brewery,
					'style' : style,
					'abv' : abv,
					'rating' : float(rating),
					'r_dev' : r_dev
				})

		index += 50


if __name__ == '__main__':
	# Parse the urls for the top 250 reviewers
	user_urls = parse_top_reviewers()
	first = True
	with open('beeradvocate_reviews.txt', 'a+') as file:
		file.write('[\n')
		for user in user_urls:
			try:
				reviews = parse_reviews(user)
				if reviews:
					if not first:
						file.write(',\n')
					json.dump({'user': user,
							   'reviews': reviews}, file, encoding='utf8')
					first = False
			except:
				continue
		file.write('\n]')

