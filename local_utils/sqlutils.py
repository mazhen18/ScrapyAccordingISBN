import pymysql
from local_utils.myutils import get_log_msg


TABLE_NAME_BASE_INFOS = 'book_base_info'


def connect_mysql():
    db = pymysql.connect(host="localhost", user="root",
                         password="575730622", db="bookinfos", port=3306)
    return db


def query_list_isbn(list_isbn):
    sql = "select * from %s where isbn13='%s'" % (TABLE_NAME_BASE_INFOS, list_isbn[0])

    for isbn in list_isbn[1:]:
        sql += (" or isbn13='%s'" % isbn)

    try:
        return excute_query_sql(sql)
    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))


def update_bookbaseinfos(ditc_bookbaseinfos):
    table_name = 'book_base_info'

    sql = generate_update_sql(table_name, ditc_bookbaseinfos, ditc_bookbaseinfos.get('isbn13'))

    try:
        excute_no_query_sql(sql)
    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))


def insert_bookbaseinfos(ditc_bookbaseinfos):
    table_name = 'book_base_info'

    sql = generate_insert_sql(table_name, ditc_bookbaseinfos)
    try:
        excute_no_query_sql(sql)
    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))


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

        if len(results) == 0:
            return ['']
        else:
            if results[0][0] == '':
                return ['']
            else:
                return results

    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))
    finally:
        db.close()


def excute_no_query_sql(sql):
    db = connect_mysql()
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()  # 提交当前事务
    except pymysql.Error as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))
    finally:
        db.close()


def query_title(isbn13):

    sql = "select title from %s where isbn13='%s'" % (TABLE_NAME_BASE_INFOS, isbn13)

    try:
        return excute_query_sql(sql)
    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))


def query_trans_name(title):
    sql = "select trans_name from %s where title='%s'" % (TABLE_NAME_BASE_INFOS, title)

    try:
        return excute_query_sql(sql)
    except Exception as e:
        raise Exception(('%s' % e) + get_log_msg('insert_bookbaseinfos', 'sql=%s' % sql))


def check_sql_str(str):
    #处理单引号
    try:
        after_str = str.replace('\'', '\'\'')
        return after_str
    except Exception as e:
        raise Exception(get_log_msg('check_sql_str', 'str=%s,e.msg=%s' % (str, e)))
