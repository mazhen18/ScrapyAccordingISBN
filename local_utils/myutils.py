from api.query_isbn import query_isbn
import yaml
import logging.config
import os
import re
import requests
import datetime
from local_utils.pathutils import get_project_path
import execjs
from proxy.proxies import update_spider_proxies
from local_utils import pathutils


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
    if len(list_contain_isbn13) == 0:
        return True
    else:
        list_timestamp = []
        for contain_isbn13 in list_contain_isbn13:
            list_timestamp.append(contain_isbn13.split('>')[0].strip())
        list_timestamp.sort(reverse=True)
        last_timestamp = list_timestamp[0]
        d1 = datetime.datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        d2 = datetime.datetime.strptime(get_current_timestamp('-m'), '%Y-%m-%d %H:%M:%S.%f')
        delta = d2 - d1
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


def append_unfound_isbn13_to_txt(isbn13):
    txt_path = pathutils.get_unfound_isbn13_txt_path()
    #删除isbn13所在行
    isbn13_row_num_list = get_row_num_list(isbn13, txt_path)

    delete_special_lines_in_txt(isbn13_row_num_list, txt_path)

    with open(txt_path, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(('%s > %s\n' % (get_current_timestamp('-m'), isbn13)) + content)


def delete_special_lines_in_txt(isbn13_row_num_list, txt_path):
    files = open(txt_path, 'r+')
    line_list = files.readlines()

    for row_num in isbn13_row_num_list:
        line_list[row_num] = ''

    files.close()

    files = open(txt_path, 'w+')
    files.writelines(line_list)

    files.close()

def get_row_num_list(isbn13, txt_path):
    isbn13_row_num_list = []
    with open(txt_path, 'r+') as f:
        for i, line in enumerate(f.readlines()):
            if line.find(isbn13) != -1:
                isbn13_row_num_list.append(i)
        return isbn13_row_num_list


def get_current_timestamp(type='-m'):
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

    last_modify_time = datetime.datetime.strptime('%s' % last_modify_time, '%Y-%m-%d %H:%M:%S.%f')

    current_time = datetime.datetime.strptime(get_current_timestamp('-m'), '%Y-%m-%d %H:%M:%S.%f')

    delta = current_time - last_modify_time

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
