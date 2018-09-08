# coding=utf-8
from bs4 import BeautifulSoup
from local_utils.myutils import get_log_msg


def get_element_from_bs4html(domain, html_soup):

    try:
        if domain == 'taobao':
            return html_soup.find('div', {'id': 'mainsrp-itemlist'})\
                .findAll('div', {'class': "row row-2 title"})
    except:
        return ''

def get_detail_data_from_bs4html(domain, html_soup, search_type):

    try:
        if domain == 'taobao':
            if search_type == 'classfication':
                return html_soup.find('ul', {'id': 'J_AttrUL'}).findAll('li')[2].get_text()

    except Exception as e:
        return ''