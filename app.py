from flask import Flask, jsonify, request
from db import get_connection

app = Flask(__name__)

COLUNAS = ['logradouro', 'tipo_logradouro', 'bairro', 'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
CAMPOS_OBRIGATORIOS = ['logradouro', 'cidade']


@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis")
            imoveis = cursor.fetchall()
        return jsonify(imoveis), 200
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)