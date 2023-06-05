# this is a file to randomly generate collections using items
# some are generic, some are specific
#   - specific: about one item type (movies/books/songs)
#   - generic: about multiple item types 



import datetime
import random
import sqlite3

conn = sqlite3.connect('../instance/db.sqlite')
c = conn.cursor()

user_ids = [
    4,
    5,
    6,
    7,
    8,
    9,
    10,
]

collection_names = {
    "movies": [
        "Best Movies of All Time",
        "You Should Watch These Movies",
        "Movies I've Watched",
    ],
    "books": [
        "Best Books of All Time",
        "You Should Read These Books",
        "Books I've Read",
    ],
    "songs": [
        "Best Songs of All Time",
        "You Should Listen to These Songs",
        "Songs I've Listened To",
    ],
    "generic": [
        "Best Items of All Time",
        "You Should Check These Out",
        "Items I've Seen",
    ],
}

collection_descriptions = {
    "movies": [
        "These are the best movies of all time. You should watch them.",
        "These are some movies I've watched. You should watch them too.",
        "These are some movies I've watched. You should watch them too.",
    ],
    "books": [
        "These are the best books of all time. You should read them.",
        "These are some books I've read. You should read them too.",
        "These are some books I've read. You should read them too.",
    ],
    "songs": [
        "These are the best songs of all time. You should listen to them.",
        "These are some songs I've listened to. You should listen to them too.",
        "These are some songs I've listened to. You should listen to them too.",
    ],
    "generic": [
        "These are the best items of all time. You should check them out.",
        "These are some items I've seen. You should check them out too.",
        "These are some items I've seen. You should check them out too.",
    ],
}


# get all the items
items = c.execute("SELECT * FROM item").fetchall()
items_by_type = {
    "movies": [],
    "books": [],
    "songs": [],
}

# sort items by type
for item in items:
    if item[3] == "movie":
        items_by_type["movies"].append(item)
    elif item[3] == "book":
        items_by_type["books"].append(item)
    elif item[3] == "song":
        items_by_type["songs"].append(item)

def populate_collections():
    # go through each user
    for user_id in user_ids:
        # random chance to have a generic collection
        if random.randint(0, 1) == 0:
            
            # create collection
            name = collection_names["generic"][random.randint(0, 2)]
            description = collection_descriptions["generic"][random.randint(0, 2)]
            created_timestamp = datetime.datetime.now()
            updated_timestamp = datetime.datetime.now()

            # add collection to db
            c.execute("INSERT INTO collection (name, description, user_id, is_fork, created_timestamp, updated_timestamp) VALUES (?, ?, ?, false, ?, ?)", (name, description, user_id, created_timestamp, updated_timestamp))
            collection_id = c.lastrowid

            # add 10 items to collection
            for item in random.choices(items, k=random.randint(1, 10)):
                added_timestamp = datetime.datetime.now()
                print(item[0])
                c.execute("INSERT INTO collection_item (collection_id, item_id, added_timestamp) VALUES (?, ?, ?)", (collection_id, item[0], added_timestamp))

        # random chance to have a specific collection
        if random.randint(0, 5) >= 2:

            # choose item type
            item_type = random.choice(["movies", "books", "songs"])

            # create collection
            name = collection_names[item_type][random.randint(0, 2)]
            description = collection_descriptions[item_type][random.randint(0, 2)]
            created_timestamp = datetime.datetime.now()
            updated_timestamp = datetime.datetime.now()
            
            # add collection to db
            c.execute("INSERT INTO collection (name, description, user_id, is_fork, created_timestamp, updated_timestamp) VALUES (?, ?, ?, false, ?, ?)", (name, description, user_id, created_timestamp, updated_timestamp))
            collection_id = c.lastrowid

            # add 10 items to collection
            for item in random.choices(items_by_type[item_type], k=random.randint(1, 10)):
                added_timestamp = datetime.datetime.now()
                c.execute("INSERT INTO collection_item (collection_id, item_id, added_timestamp) VALUES (?, ?, ?)", (collection_id, item[0], added_timestamp))
        
populate_collections()  

# save changes
conn.commit()
conn.close()
