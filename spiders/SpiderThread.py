import threading
from utils.scrapyutils import scrap_bookinfs


class SpiderThread(threading.Thread):
    """"""

    def __init__(self, name, isbn):
        """Constructor"""
        threading.Thread.__init__(self)
        self.name = name
        self.isbn = isbn

    def run(self):
        scrap_bookinfs(self.isbn)
