# from local_utils.myutils import get_log_msg
import urllib.request
import ssl
import json
import logging

logger = logging.getLogger('query_isbn')


def query_isbn(isbn, company_code=1):
    if company_code == 1:
        return query_isbn_1(isbn)
    elif company_code == 2:
        return query_isbn_2(isbn)


#杭州网尚科技有限公司
def query_isbn_1(isbn):
    host = 'http://aliapi63.jisuapi.com'
    path = '/isbn/query'
    # method = 'GET'
    appcode = 'a0ede7bb030d402593334d6a15c9bdbf'
    querys = 'isbn=' + isbn
    # bodys = {}
    url = host + path + '?' + querys

    request = urllib.request.Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    msg = ''
    try:
        response = urllib.request.urlopen(request, context=ctx)
        book_infos = json.loads(response.read())
        status = book_infos.get('status')
        if status == '0':
            return book_infos.get('result')
        else:
            # msg = get_log_msg('query_isbn_1',
            #                            'query failure isbn:%s, error statu code:%s' % (isbn, status))
            # logger.warning(msg)
            return None
    except Exception as e:
        # logger.warning(('%s' % e) + get_log_msg('query_isbn_1',
        #                                          'query failure isbn:%s, error statu code:%s' % (isbn, status)))
        return None


#北京库斯曼科技有限公司
def query_isbn_2(isbn):

    host = 'http://isbn.market.alicloudapi.com'
    path = '/ISBN'
    # method = 'GET'
    appcode = 'a0ede7bb030d402593334d6a15c9bdbf'
    querys = 'is_info=0&isbn=%s' % isbn
    # bodys = {}
    url = host + path + '?' + querys

    request = urllib.request.Request(url)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    response = urllib.request.urlopen(request)
    book_infos = json.loads(response.read())
    error_code = book_infos.get('error_code')
    if error_code == 0:
        return book_infos.get('result')
    else:
        logger.warning('fun:query_isbn_2, '
                       'query failure isbn:%s, '
                       'error code:%s'
                       % (isbn, error_code))
        return None
