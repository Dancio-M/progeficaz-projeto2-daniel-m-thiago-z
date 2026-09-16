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

@app.route('/imoveis/tipo/<string:tipo>', methods=['GET'])
def buscar_por_tipo(tipo):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis WHERE tipo = %s", (tipo,))
            imoveis = cursor.fetchall()
        return jsonify(imoveis), 200
    finally:
        conn.close()

@app.route('/imoveis/cidade/<string:cidade>', methods=['GET'])
def buscar_por_cidade(cidade):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
            imoveis = cursor.fetchall()
        return jsonify(imoveis), 200
    finally:
        conn.close()

@app.route('/imoveis', methods=['POST'])
def criar_imovel():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido ou ausente'}), 400

    faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in dados]
    if faltando:
        return jsonify({'erro': f'Campos obrigatórios ausentes: {", ".join(faltando)}'}), 400

    campos = [c for c in COLUNAS if c in dados]
    valores = [dados[c] for c in campos]
    placeholders = ', '.join(['%s'] * len(campos))
    colunas_sql = ', '.join(campos)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO imoveis ({colunas_sql}) VALUES ({placeholders})",
                valores,
            )
            novo_id = cursor.lastrowid
            cursor.execute("SELECT * FROM imoveis WHERE id = %s", (novo_id,))
            imovel = cursor.fetchone()
        return jsonify(imovel), 201
    finally:
        conn.close()

@app.route('/imoveis/<int:imovel_id>', methods=['PUT'])
def atualizar_imovel(imovel_id):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido ou ausente'}), 400

    campos = [c for c in COLUNAS if c in dados]
    if not campos:
        return jsonify({'erro': 'Nenhum campo válido para atualizar'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if not imovel_existe(cursor, imovel_id):
                return jsonify({'erro': 'Imóvel não encontrado'}), 404

            set_sql = ', '.join([f"{c} = %s" for c in campos])
            valores = [dados[c] for c in campos] + [imovel_id]
            cursor.execute(f"UPDATE imoveis SET {set_sql} WHERE id = %s", valores)

            cursor.execute("SELECT * FROM imoveis WHERE id = %s", (imovel_id,))
            imovel = cursor.fetchone()
        return jsonify(imovel), 200
    finally:
        conn.close()

@app.route('/imoveis/<int:imovel_id>', methods=['DELETE'])
def remover_imovel(imovel_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if not imovel_existe(cursor, imovel_id):
                return jsonify({'erro': 'Imóvel não encontrado'}), 404
            cursor.execute("DELETE FROM imoveis WHERE id = %s", (imovel_id,))
        return '', 204
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)