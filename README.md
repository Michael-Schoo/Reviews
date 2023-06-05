# Reviews

A website that allows users to review things (ie movies)

For some API end points, look at [routes.md](./routes.md).

## Commands
### Virtual Env
**Windows:** `.venv/Scripts/activate.bat`

### Run
```sh
python .
```

### Database
```sh
flask db init

flask db upgrade
flask db migrate -m "description"
```

# Notes:
 * some images and item data have been sourced wikipedia and imdb [populate_db.py](./populate_db.py)
