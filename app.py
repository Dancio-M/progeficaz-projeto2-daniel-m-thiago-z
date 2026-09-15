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

def imovel_existe(cursor, imovel_id):
    cursor.execute("SELECT id FROM imoveis WHERE id = %s", (imovel_id,))
    return cursor.fetchone() is not None


@app.route('/imoveis/<int:imovel_id>', methods=['GET'])
def obter_imovel(imovel_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis WHERE id = %s", (imovel_id,))
            imovel = cursor.fetchone()
        if imovel is None:
            return jsonify({'erro': 'Imóvel não encontrado'}), 404
        return jsonify(imovel), 200
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)