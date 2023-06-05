from datetime import datetime
import imdb
import sqlite3

# import the database
conn = sqlite3.connect('../instance/db.sqlite')
c = conn.cursor()

# use the imdb package to get the top 100 movies (still data scraping)
ia = imdb.IMDb()
top_movies = ia.get_top250_movies()

# only get the top 100 movies
for i in range(100):
    print(f"MOVIE: {i+1}. {top_movies[i]}")
    movie = ia.get_movie(top_movies[i].getID())

    # Table: item
    description = movie["plot"][0]
    name = movie["original title"]
    type = "movie"
    created_timestamp = datetime.utcnow()
    updated_timestamp = datetime.utcnow()
    image_url = movie["full-size cover url"]

    # Table: movie
    year = movie["year"]
    director = str(movie["director"][0])
    length = movie["runtimes"][0]

    # add to database
    c.execute("INSERT INTO item (description, name, type, created_timestamp, updated_timestamp, image_url) VALUES (?, ?, ?, ?, ?, ?)", (description, name, type, created_timestamp, updated_timestamp, image_url))

    item_id = c.lastrowid
    c.execute("INSERT INTO movie (year, director, length, id) VALUES (?, ?, ?, ?)", (year, director, length, item_id))
    
# save changes
conn.commit()
conn.close()
