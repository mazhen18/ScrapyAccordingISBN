import os


def get_project_path():
    cur_file_path = os.path.abspath(__file__)
    project_path = os.path.dirname(os.path.dirname(cur_file_path))
    return project_path


def get_virtualenv_python_path():
    project_path = get_project_path()
    return project_path + '/venv/bin/python'


def get_spider_path(spider_name):
    project_path = get_project_path()

    spider_path = project_path + '/isbnSpider/isbnSpider/spiders/' + spider_name + "_spider.py"

    return spider_path


def get_run_spider_path():

    project_path = get_project_path()

    run_spider_path = project_path + '/spiders/isbnSpider/isbnSpider/run_spider.py'

    return run_spider_path


def get_unfound_isbn13_txt_path():
    return get_project_path() + "/log/unfound_isbn13.txt"


def get_proxies_txt_path():
    return get_project_path() + "/proxy/proxies.txt"

