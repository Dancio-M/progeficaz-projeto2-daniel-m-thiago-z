from db import get_connection

with open('imoveis.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

conn = get_connection()
try:
    with conn.cursor() as cursor:
        for comando in sql_script.split(';'):
            comando = comando.strip()
            if comando and not comando.startswith('--'):
                cursor.execute(comando)
    print("Banco populado com sucesso!")
finally:
    conn.close()