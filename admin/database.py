import pymysql
import os
from dotenv import load_dotenv

_connection = None


def get_connection():
    load_dotenv()
    global _connection

    timeout = 10
    if _connection is None:
        try:
            _connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=timeout,
                cursorclass=pymysql.cursors.DictCursor,
                db="defaultdb",
                host=os.getenv('HOST'),
                password=os.getenv('PASSWORD'),
                read_timeout=timeout,
                port=16947,
                user='avnadmin',
                write_timeout=timeout,
            )
        except Exception as e:
            print("Database connection failed:", e)
            return None

    return _connection


def send_data_to_db(data):
    conn = get_connection()
    query = '''
        INSERT INTO manual (id, outcomes, title, apparatus, theory, procedures, result, precautions, qna, link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    params = (
        data['id'],
        data['outcomes'],
        data['title'],
        data['apparatus'],
        data['theory'],
        data['procedures'],
        data['result'],
        data['precautions'],
        data['qna'],
        data['link']
    )

    with conn.cursor() as cursor:
        cursor.execute(query, params)
        conn.commit()



def get_manual(manual_id):
    conn = get_connection()
    query = '''
        SELECT * FROM manual WHERE id = %s
    '''
    params = (manual_id,)
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()
