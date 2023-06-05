from datetime import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup

# import the database
conn = sqlite3.connect('../instance/db.sqlite')
c = conn.cursor()

# get the top songs from wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify'
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
    
    # get the name of the song (and try to get its wikipedia url)
    name_obj = row.find('th').find('a')
    name_url = name_obj['href'].replace('/wiki/', '')
    name = name_obj['title']
    length = 'unknown'

    # get the artist and year from the other columns
    artist = cols[1].text.strip()
    year = cols[3].text.strip()

    # if there isn't a link, skip
    if name_url is None:
        continue

    # get description and image_url from wikipedia
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
    c.execute("INSERT INTO item (description, name, type, created_timestamp, updated_timestamp, image_url) VALUES (?, ?, ?, ?, ?, ?)", (description, name, 'song', created_timestamp, updated_timestamp, image_url))

    # Table book: year, artist, length
    item_id = c.lastrowid
    c.execute("INSERT INTO song (year, artist, length, id) VALUES (?, ?, ?, ?)", (year, artist , length, item_id))

# save changes
conn.commit()
conn.close()
