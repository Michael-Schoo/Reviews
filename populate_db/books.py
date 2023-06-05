from datetime import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup

# import the database
conn = sqlite3.connect('../instance/db.sqlite')
c = conn.cursor()

# get the top books from the wikipedia page
url = 'https://en.wikipedia.org/wiki/Bokklubben_World_Library'
html = requests.get(url).content
soup = BeautifulSoup(html)

table = soup.find_all('table')[0]
rows = table.find_all('tr')

# go through each row
for row in rows:
    # get columns (and skip if there aren't 5)
    cols = row.find_all('td')
    if (len(cols) != 5):
        continue
    
    # get data by column of the table
    name, author, year, country, language = [ele.text.strip() for ele in cols]

    # if there isn't a link, skip
    if cols[0].find('a') is None:
        continue
    
    # get the url for the item
    name_url = cols[0].find('a')['href'].replace('/wiki/', '')

    # the url for the api request to get more info
    request_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name_url}"
    request = requests.get(request_url)
    if request.status_code != 200:
        print(f"ERROR: {request.status_code}")
        continue

    # get the extra data from the api
    data = request.json()
    description = data['extract']
    image_url = data.get('originalimage', {}).get('source', None)

    # Table item: name, author, description, created_timestamp, updated_timestamp, image_url
    created_timestamp = datetime.utcnow()
    updated_timestamp = datetime.utcnow()

    # add to database
    c.execute("INSERT INTO item (description, name, type, created_timestamp, updated_timestamp, image_url) VALUES (?, ?, ?, ?, ?, ?)", (description, name, 'book', created_timestamp, updated_timestamp, image_url))

    # Table book: year, country, language
    item_id = c.lastrowid
    c.execute("INSERT INTO book (year, country, language, author, id) VALUES (?, ?, ?, ?, ?)", (year, country, language, author, item_id))

# save changes
conn.commit()
conn.close()
