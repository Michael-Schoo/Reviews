# Routes

## Table of Contents

- [Routes](#routes)
  - [Table of Contents](#table-of-contents)
  - [Data Types](#data-types)
    - [User Type](#user-type)
    - [Collection](#collection)
    - [Item](#item)
    - [Book (item)](#book-item)
    - [Movie (item)](#movie-item)
    - [Song (item)](#song-item)
    - [Comment](#comment)
    - [Success](#success)
  - [User](#user)
    - [`POST` /login](#post-login)
    - [`POST` /register](#post-register)
    - [`GET` /settings/2fa](#get-settings2fa)
    - [`POST` /settings/2fa](#post-settings2fa)
    - [`PATCH` /settings/details](#patch-settingsdetails)
    - [`PATCH` /settings/password](#patch-settingspassword)
    - [`GET` /user/@me](#get-userme)
    - [`GET` /user/{id}](#get-userid)
  - [Collections](#collections)
    - [`GET` /collections](#get-collections)
    - [`GET` /collection/{id}](#get-collectionid)
    - [`POST/PATCH` /collection/{id}](#postpatch-collectionid)
    - [`DELETE` /collection/{id}](#delete-collectionid)
    - [`GET` /collection/{id}/items](#get-collectioniditems)
    - [`GET` /collection/{id}/item/{id}](#get-collectioniditemid)
    - [`POST/DELETE` /collection/{id}/item/{id}](#postdelete-collectioniditemid)
    - [`POST` /collection/{id}/fork](#post-collectionidfork)
    - [`POST` /collection/{id}/like](#post-collectionidlike)
    - [`POST` /collection/{id}/unlike](#post-collectionidunlike)
  - [Items](#items)
    - [`GET` /items](#get-items)
    - [`GET` /item/{id}](#get-itemid)
    - [`POST/PATCH` /item/{id}](#postpatch-itemid)
    - [`DELETE` /item/{id}](#delete-itemid)
  - [Comments (item and collection)](#comments-item-and-collection)
    - [`GET` /(collection|item)/{id}/comments](#get-collectionitemidcomments)
    - [`POST` /(collection|item)/{id}/comment](#post-collectionitemidcomment)
    - [`DELETE` /(collection|item)/{id}/comment/{id}](#delete-collectionitemidcommentid)
    - [`PATCH` /(collection|item)/{id}/comment/{id}](#patch-collectionitemidcommentid)

## Data Types

### User Type

```json
{
    "id": 1234,
    "username": "username",
    "name": "name",
    "gravatar": "https://www.gravatar.com/avatar/...",
    "admin": false, // Can be true
}
```

### Collection

```json
{
    "id": 1234,
    "name": "name",
    "description": "description",
    "forked_from": Collection, // if second level it is just the id
    "is_fork": false,
    "created_timestamp": "Mon, 1 Jan 2023 00:00:01 GMT",
    "updated_timestamp": "Mon, 1 Jan 2023 00:00:01 GMT",
    "user": User, // if second level it is just the id
    "user_id": 1234,
    "items": Item[], // if second level it is just the ids
    "forks": Collection[], // if second level it is just the ids
}
```

### Item

```json
{
    "id": 1234,
    "name": "name",
    "description": "description",
    "type": "book", // book/movie/song
    "collections": Collection[], // forks and user is just the ids
    // Either of the following:
    "book": Book,
    "movie": Movie,
    "song": Song,
```

### Book (item)

```json
{
    "id": 1234,
    "author": "author",
    "year": 2023,
    "language": "English",
    "country": "United States"
}    
```

### Movie (item)

```json
{
    "id": 1234,
    "director": "director",
    "year": 2023,
    "length": 123,
}    
```

### Song (item)

```json
{
    "id": 1234,
    "artist": "artist",
    "year": 2023,
    "length": 123, // In minutes
}    
```

### Comment

```json
{
    "id": 1234,

    "comment": "text",
    "timestamp": "Mon, 1 Jan 2023 00:00:01 GMT",
    "user": User, // if second level it is just the id
    "user_id": 1234,

    // Either of the following:
    "collection": Collection, // if second level it is just the id
    "collection_id": 1234,

    "item": Item, // if second level it is just the id
    "item_id": 1234,

}
```

### Success

```json
{
    "success": true
}
```

## User

### `POST` /login

Request body:

```json
{
    "email": "username",
    "password": "password",
    "code": 123456 // Required if 2FA is enabled
}
```

Successful response: [User](#user-type)

### `POST` /register

Request body:

```json
{
    "username": "username",
    "password": "password",
    "email": "me@gmail.com",
    "name": "name",
}
```

Successful response: [User](#user-type)

### `GET` /settings/2fa

Requires:

- Account logged in

Successful response:

```json
{
    "qr_url": "otpauth://totp/Example:me@gmail.com?secret=XXXXXXXXXXXXXXXX&issuer=Example",
    "secret": "XXXXXXXXXXXXXXXX",
    "already_set": false // Can be true
}
```

### `POST` /settings/2fa

Requires:

- Account logged in

Request body:

```json
{
    "code": 123456,
    "secret": "XXXXXXXXXXXXXXXX",
}
```

### `PATCH` /settings/details

Requires:

- Account logged in

Request body:

```json
{
    "username": "username",
    "email": "me@gmail.com",
    "name": "name",
}
```

### `PATCH` /settings/password

Requires:

- Account logged in

Request body:

```json
{
    "old_password": "password",
    "new_password": "password123",
    "new_password_confirm": "password123",
}
```

Successful response: [Success](#success)

### `GET` /user/@me

Requires:

- Account logged in

Successful response: [User](#user-type)

### `GET` /user/{id}

Successful response: [User](#user-type)

## Collections

### `GET` /collections

Successful response: [Collection[]](#collection)

### `GET` /collection/{id}

Successful response: [Collection](#collection)

### `POST/PATCH` /collection/{id}

Requires:

- Account logged in
- Collection owner

Request body: [Collection](#collection)

Successful response: [Collection](#collection)

### `DELETE` /collection/{id}

Requires:

- Account logged in
- Collection owner

Successful response: [Success](#success)

### `GET` /collection/{id}/items

Successful response: [Item[]](#item)

### `GET` /collection/{id}/item/{id}

Successful response:

```json
{
    "exists": true,
}
```

### `POST/DELETE` /collection/{id}/item/{id}

Requires:

- Account logged in
- Collection owner

Successful response: [Success](#success)

### `POST` /collection/{id}/fork

Requires:

- Account logged in

Successful response: [Collection](#collection)

### `POST` /collection/{id}/like

Requires:

- Account logged in

Successful response: [Success](#success)

### `POST` /collection/{id}/unlike

Requires:

- Account logged in

Successful response: [Success](#success)

## Items

### `GET` /items

Successful response: [Item[]](#item)

### `GET` /item/{id}

Successful response: [Item](#item)

### `POST/PATCH` /item/{id}

Requires:

- Account logged in
- Admin

Request body: [Item](#item)

Successful response: [Item](#item)

### `DELETE` /item/{id}

Requires:

- Account logged in
- Admin

Successful response: [Success](#success)

## Comments (item and collection)

### `GET` /(collection|item)/{id}/comments

Successful response: [Comment[]](#comment)

### `POST` /(collection|item)/{id}/comment

Requires:

- Account logged in

Request body:

```json
{
    "comment": "text",
}
```

Successful response: [Comment](#comment)

### `DELETE` /(collection|item)/{id}/comment/{id}

Requires:

- Account logged in
- Comment owner

Successful response: [Success](#success)

### `PATCH` /(collection|item)/{id}/comment/{id}

Requires:

- Account logged in
- Comment owner

Request body:

```json
{
    "comment": "text",
}
```

Successful response: [Comment](#comment)
