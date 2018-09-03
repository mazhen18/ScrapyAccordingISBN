import pymysql
import logging
logger = logging.getLogger("sqlutils")

TABLE_NAME_BASE_INFOS = 'book_base_info'


def connect_mysql():
    db = pymysql.connect(host="localhost", user="root",
                         password="575730622", db="bookinfos", port=3306)
    return db


def query_list_isbn(list_isbn):
    sql = "select * from %s where isbn13='%s'" % (TABLE_NAME_BASE_INFOS, list_isbn[0])

    for isbn in list_isbn[1:]:
        sql += (" or isbn13='%s'" % isbn)

    return excute_query_sql(sql)


def update_bookbaseinfos(ditc_bookbaseinfos):
    table_name = 'book_base_info'

    sql = generate_update_sql(table_name, ditc_bookbaseinfos, ditc_bookbaseinfos.get('isbn13'))

    excute_no_query_sql(sql)


def insert_bookbaseinfos(ditc_bookbaseinfos):
    table_name = 'book_base_info'

    sql = generate_insert_sql(table_name, ditc_bookbaseinfos)

    excute_no_query_sql(sql)


def generate_insert_sql(table_name, dict_data):
    sql_key = ','.join(dict_data.keys())

    value_list = list(dict_data.values())
    sql_value = "'%s'" % value_list[0]
    for value in value_list[1:]:
        sql_value += ",'%s'" % value

    sql = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, sql_key, sql_value)

    return sql


def generate_update_sql(table_name, dict_data, isbn13):
    t = ('isbn13', isbn13)
    sql = 'UPDATE %s SET ' % table_name \
          + ','.join(['%s=%r' % (k, dict_data[k]) for k in dict_data]) \
          + ' WHERE %s=%r;' % (t[0], t[1])
    return sql


def excute_query_sql(sql):
    db = connect_mysql()
    cur = db.cursor()

    try:
        cur.execute(sql)  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录

        return results

    except Exception as e:
        logger.error('func:excute_query_sql, sql=%s, e.msg=%s' % (sql, e))
        raise e
    finally:
        db.close()


def excute_no_query_sql(sql):
    db = connect_mysql()
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()  # 提交当前事务
    except pymysql.Error as e:
        logger.error('func:excute_no_query_sql, sql=%s, e.msg=%s' % (sql, e))
        raise e
    finally:
        db.close()
