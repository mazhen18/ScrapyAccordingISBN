import threading

from api.query_isbn import query_isbn
import yaml
import logging.config
import os
import re
import requests
import datetime

from local_utils.data_check_utils import check_data_validity
from local_utils.pathutils import get_project_path
import execjs
from proxy.proxies import update_spider_proxies
from local_utils import pathutils

write_lock = threading.Lock()

def query_book_infos(isbn, company_code=1):
    return query_isbn(isbn, company_code)


def init_logging():
    def setup_logging(default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
        log_spider_dir = get_project_path() + "/spiders/log/"
        # log_dir = get_project_path() + "/log/"
        log_dirs_list = ['info', 'debug', 'warning', 'error']
        for dir in log_dirs_list:
            # log_path = log_dir + dir
            log_spider_path = log_spider_dir + dir
            # if not os.path.exists(log_path):
            #     os.makedirs(log_path)
            if not os.path.exists(log_spider_path):
                os.makedirs(log_spider_path)

        path = default_path
        # value = os.getenv(env_key, None)
        # if value:
        #     path = value
        if os.path.exists(path):
            with open(path, "r") as f:
                logging.config.dictConfig(yaml.load(f))
        else:
            logging.basicConfig(level=default_level)
    setup_logging(get_project_path() + "/setting/logging.yaml")


def get_unfound_list_flag(isbn13):
    unfound_isbn13_list = get_list_from_txt(pathutils.get_unfound_isbn13_txt_path())
    list_contain_isbn13 = []
    for unfound_isbn13 in unfound_isbn13_list:
        if unfound_isbn13.find(isbn13) != -1:
            list_contain_isbn13.append(unfound_isbn13)
    if len(list_contain_isbn13) == 0:#说明该ISBN13没有被查询过，或者查询过但是只要部分信息没查询到
        return True
    else:
        #如果之前该isbn13就查询不到，那么就看最近一次查询时间，
        # 如果最近一次查询时间到现在间隔小于5天就不在重复查询
        list_timestamp = []
        for contain_isbn13 in list_contain_isbn13:
            list_timestamp.append(contain_isbn13.split('>')[0].strip())
        list_timestamp.sort(reverse=True)
        last_timestamp = list_timestamp[0]
        delta = get_time_span_cmp_curr('%s' % last_timestamp, '-m')
        return True if delta.days > 5 else False #间隔5天后可以再次查询


def check_isbn(isbn13):
    len_isbn = len(isbn13)
    len_flag = (len_isbn == 13 or len_isbn == 10) and isbn13.isdigit()
    unfound_list_flag = get_unfound_list_flag(isbn13)
    return len_flag and unfound_list_flag


def obj2dict(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr


def contain_zh(word):
    '''
    判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    '''
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    word = word.decode()
    match = zh_pattern.search(word)

    return match


def find_first_digit(str):
    for i, c in enumerate(str):
        if c.isdigit():
            return i
    return None


class Py4Js():

    def __init__(self):
        self.ctx = execjs.compile("""
        function TL(a) {
        var k = "";
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };

    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
    """)

    def getTk(self, text):
        return self.ctx.call("TL", text)


def google_translate(content):
    rows_len = len(content.splitlines())

    if rows_len != 1 or len(content) > 4891:
        raise Exception(get_log_msg('google_translate', 'invalid argument:%s' % content))

    param = {'tk': Py4Js().getTk(content), 'q': content}

    result = requests.get("""http://translate.google.cn/translate_a/single?client=t&sl=en
        &tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss
        &dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1&srcrom=0&ssel=0&tsel=0&kc=2""", params=param)

    try:
        return result.json()[0][0][0]
    except IndexError as e:
        raise IndexError(get_log_msg('google_translate', e))


def get_log_msg(function_name, cur_msg):
    str = '\n ==> [%s] msg=%s\n' % (function_name, cur_msg)
    return '%s' % str


def get_valid_search_text(text):

    result = text
    if len(text) > 50:
        text = text[:50]
        result = ' '.join(text.split(' ')[:-1])
    return result


def get_isbn13_list_from_txt(path):
    return get_list_from_txt(path)


def get_list_from_txt(path):
    txt_list = []
    with open(path, "r") as f:
        lines = f.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            txt_list.append(line.strip())
        return txt_list


def update_unfound_isbn13_to_txt(isbn13, type='d'):
    write_lock.acquire()
    txt_path = pathutils.get_unfound_isbn13_txt_path()

    content = get_list_from_txt(txt_path)

    count = 0
    for i, line in enumerate(content):
        if line.find(isbn13) != -1:
            content[i] = ''
            count += 1

    if type == 'i':
        content.insert(0, '%s > %s' % (get_current_timestamp_str('-m'), isbn13))

    if not (type == 'd' and count == 0):

        with open(txt_path, 'w') as f:

            f.write('\n'.join(content))

    write_lock.release()



def get_current_timestamp_str(type='-m'):
    if type == 'm':
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    elif type == 's':
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    elif type == '-m':
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    else:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def update_proxies_txt():
    last_modify_time = os.path.getmtime(pathutils.get_proxies_txt_path())
    last_modify_time = datetime.datetime.fromtimestamp(last_modify_time)

    delta = get_time_span_cmp_curr('%s' % last_modify_time, '-m')

    if delta.days > 2:
        update_spider_proxies()


def logger(type='i'):

    if type == 'i':
        return logging.getLogger('infoLogger')
    if type == 'd':
        return logging.getLogger('debugLogger')
    if type == 'w':
        return logging.getLogger('warningLogger')
    if type == 'e':
        return logging.getLogger('errorLogger')


def get_datetime_from_str(timestamp, formate='m'):
    date_time = ''
    if formate == '-m':
        date_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    if formate == 'm':
        date_time = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S%f')
    if formate == '-s':
        date_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    if formate == 's':
        date_time = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S')
    return date_time


def get_time_span_cmp_curr(timestamp_str, formate='m'):
    cmp_time = get_datetime_from_str('%s' % timestamp_str, formate)

    current_time = get_datetime_from_str(get_current_timestamp_str(formate), formate)

    return current_time - cmp_time


def get_xpath_result(response, spider_name, xpath_list):

    result = ''

    for xpath in xpath_list:

        data = response.xpath(xpath).extract()

        if data:
            result = data[0]
            break

    return check_data_validity(spider_name, result)






