

import re

from flask import request


def id_from_url(url):
    """
    a function to convert "2-michael-schoo" to 2 
    """
    if '-' in url:
        return url.split('-')[0]
    else:
        return url

def url_from_id(id, name):
    """
    a function to convert id 2 and name "Michael Schoo" to "2-michael-schoo"
    """
    regex = re.compile(r'[^a-zA-Z0-9]+')
    new_text = regex.sub('-', name).strip('-')
    new_text = new_text[:50-len(str(id))-1]
    return f"{id}-{new_text}"



def wants_json_response():
    """
    returns True if the client wants a JSON response
    """
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

def get_form():
    """
    returns the form data as a dict
    """
    if wants_json_response(): return request.get_json()
    return request.form


