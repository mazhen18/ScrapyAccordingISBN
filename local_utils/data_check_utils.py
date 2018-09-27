# -*- coding: utf-8 -*-

from local_utils import myutils


def check_currency(currency):
    common_currency_char_dict = {
        '美元': '$',
        '人民币': '¥',
        '欧元': '€',
        '英镑': '￡',
        '日元': '￥',
        '法兰': '₣',
        '韩元': '₩',
        '泰铢': '฿',
        '卢币': 'руб',
        '比特币': 'B'
    }
    list_key = list(common_currency_char_dict.keys())

    list_value = list(common_currency_char_dict.values())

    try:
        index = list_value.index(currency)
        return list_value[index] + '/' + list_key[index]
    except:
        return ''


def check_trans_name(trans_name):
    # if myutils.contain_zh(trans_name):
    #     return trans_name
    # else:
    #     return ''
    return trans_name

def check_price(price):

    if price[0] == '$' and price[-1].isdigit():

        index = myutils.find_first_digit(price)

        if index:
            return price[index:]
    return ''


def check_classfication(classfication):

    try:
        class_list = classfication.split('>')
        first_class = class_list[0]
        element_list = []
        result_list = []
        for c in class_list:
            if c == first_class and len(element_list) != 0:
                result_list.append('>'.join(element_list))
                element_list = []
            element_list.append(c)
        result_list.append('>'.join(element_list))
        return '\n'.join(result_list)
    except:
        return ''


def check_data_validity(data_name, data):
    if data:
        if data_name == 'currency':
            return check_currency(data)
        elif data_name == 'trans_name':
            return check_trans_name(data)
        elif data_name == 'price':
            return check_price(data)
        elif data_name == 'classfication':
            return check_classfication(data)
    return ''


def check_href_url(domain, url):
    if domain == 'taobao':
        if url.find('http') == -1:
            return 'http:' + url

    return url
