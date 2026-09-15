import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Abre uma conexão com o MySQL hospedado no Aiven."""
    ssl_ca = os.getenv('DB_SSL_CA')
    ssl_args = {'ssl': {'ca': ssl_ca}} if ssl_ca else {'ssl': {}}

    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=DictCursor,
        autocommit=True,
        **ssl_args,
    )