from api import query_isbn
import yaml
import logging.config
import os


def query_book_infos(isbn):
    book_infos = query_isbn(isbn)
    status = book_infos.get('status')
    if status == 0:
        return book_infos.get('result')
    else:
        print()


def get_project_path():
    project_path = os.path.abspath('..')
    return project_path


def init_logging():
    def setup_logging(default_path="logging.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
        log_dir = myutils.get_project_path() + "/log/"
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




