import pymysql
import logging

logger = logging.getLogger("sqlutils")

TABLE_NAME_BASE_INFOS = 'base_infos'


def connect_mysql():
    db = pymysql.connect(host="localhost", user="amelia",
                         password="575730622", db="bookinfos", port=3306)
    return db


def query_isbn_exist(isbn):
    sql = "select isbn from %s where isbn='%s'" % (TABLE_NAME_BASE_INFOS, isbn)

    db = connect_mysql()
    cur = db.cursor()

    try:
        cur.execute(sql)  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录

        return len(results) > 0

    except Exception as e:
        logger.error("fun:query_isbn_exist,isbn=" + isbn + "e.msg=" + e)
        raise e
    finally:
        db.close()


def query_list_isbn(list_isbn):
    sql = "select * from %s where isbn='%s'" % (TABLE_NAME_BASE_INFOS, list_isbn[0])

    for isbn in list_isbn[1:]:
        sql += (" or isbn='%s'" % isbn)

    db = connect_mysql()
    cur = db.cursor()

    try:
        cur.execute(sql % (isbn))  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录

        return results

    except Exception as e:
        logger.error("fun:query_list_isbn, e.msg=" + e)
        raise e
    finally:
        db.close()
