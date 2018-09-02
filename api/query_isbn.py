import sys
import urllib.request
import ssl
import json


def query_isbn(isbn):
    host = 'http://aliapi63.jisuapi.com'
    path = '/isbn/query'
    # method = 'GET'
    appcode = 'a0ede7bb030d402593334d6a15c9bdbf'
    querys = 'isbn='+isbn
    # bodys = {}
    url = host + path + '?' + querys

    request = urllib.request.Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read()
    if (content):
        book_infos = json.loads(content)
        return book_infos
