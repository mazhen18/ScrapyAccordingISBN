from api.query_isbn import query_isbn
import yaml
import logging.config
import os
import re
import requests
import urllib.parse

from utils.pathutils import get_project_path
import execjs
logger = logging.getLogger('myutils')


def query_book_infos(isbn, company_code=1):
    return query_isbn(isbn, company_code)


def init_logging():
    def setup_logging(default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
        log_dir = get_project_path() + "/log/"
        log_dirs_list = ['info', 'debug', 'warning', 'error']
        for dir in log_dirs_list:
            path = log_dir + dir
            if not os.path.exists(path):
                os.makedirs(path)

        path = default_path
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, "r") as f:
                logging.config.dictConfig(yaml.load(f))
        else:
            logging.basicConfig(level=default_level)
    setup_logging(get_project_path() + "/setting/logging.yaml")
    return logging.getLogger("main")


def check_isbn(isbn):
    len_isbn = len(isbn)
    return (len_isbn == 13 or len_isbn == 10) and isbn.isdigit()


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
    return '\n ==> [' + function_name + '] msg=' + cur_msg + '\n'





