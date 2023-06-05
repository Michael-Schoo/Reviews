import datetime
from flask import redirect, request, jsonify
from models import Book, Movie, Song, Item
from tools.jwt_token import get_auth_user
from tools.template import render_user_template
from tools.tools import get_form, wants_json_response
from views.items import item_bp
from app import db


@item_bp.route('/item', methods=['POST'])
@item_bp.route('/item/new', methods=['GET', 'POST'])
def item_new():
    """
    New item route

    Allows users to create new items (but admin is required)
    """

    # get user (if not logged in, redirect to login page)
    user = get_auth_user()
    if user is None:
        if wants_json_response(): return jsonify(error="Unauthorized"), 401
        return redirect('/login')
    
    # admin required
    if not user.admin: return jsonify(error="Forbidden"), 403
    
    # if GET then show the form
    if request.method == 'GET':
        return render_user_template("item_new.html")
    
    # if POST, then create item
    if request.method == 'POST':
        # get the form data
        data = get_form()
        name = data.get('name')
        description = data.get('description')
        type = data.get('type')
        image_url = data.get('image_url')

        # Check if name is valid
        if not name or not type or not description:
            return jsonify(error="Invalid item", reason="Name, type, and description are required"), 400

        main_data = {
            'name': name,
            'description': description,
            # 'type': type,
            'created_timestamp': datetime.datetime.utcnow(),
            'updated_timestamp': datetime.datetime.utcnow(),
            'image_url': image_url,
        }

        # if the item is a movie
        if type == 'movie':
            # get the extra data
            director = data.get('director')
            year = data.get('year')
            length = data.get('length')
            
            # check if the extra data is valid
            if not director or not year or not length:
                return jsonify(error="Invalid movie", reason="Director, year, and length is required"), 400
            
            # make the movie (with main data and extra data)
            movie = Movie(
                **main_data,
                type='movie',
                director=director,
                year=year,
                length=length,
            )

            # add the movie to the database
            db.session.add(movie)
            db.session.commit()

            # save the id, so we can redirect to the new movie
            id = movie.id

        # if the item is a book
        elif type == 'book':
            # get the extra data
            author = data.get('author')
            year = data.get('year')
            language = data.get('language')
            country = data.get('country')

            # check if the extra data is valid
            if not author or not year or not language or not country:
                return jsonify(error="Invalid book", reason="Author, year, language, and country is required"), 400
            
            # make the book (with main data and extra data)
            book = Book(
                **main_data,
                type='book',
                author=author,
                year=year,
                language=language,
                country=country,
            )

            # add the book to the database
            db.session.add(book)
            db.session.commit()

            # save the id, so we can redirect to the new book
            id = book.id

        # if the item is a song
        elif type == 'song':
            # get the extra data
            artist = data.get('artist')
            year = data.get('year')
            length = data.get('length')
            
            # check if the extra data is valid
            if not artist or not year or not length:
                return jsonify(error="Invalid song", reason="Artist, year, and length is required"), 400
            
            # make the song (with main data and extra data)
            song = Song(
                **main_data,
                type='song',
                artist=artist,
                year=year,
                length=length,
            )

            # add the song to the database
            db.session.add(song)
            db.session.commit()

            # save the id, so we can redirect to the new song
            id = song.id

        else:
            # throw error because should never occur
            raise Exception("Invalid item type")

        # return the new data by redirecting
        item: Item = Item.query.get(id)
        return redirect(item.get_url_with_name())

