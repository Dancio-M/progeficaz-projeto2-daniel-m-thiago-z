from urllib.parse import quote

import pytest

from app import app
from db import get_connection


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def imovel_teste():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            ('Rua de Teste', 'Rua', 'Bairro Teste', 'Cidade Teste', '00000-000', 'casa', 100000.0, '2024-01-01'),
        )
        imovel_id = cursor.lastrowid
    conn.close()

    yield imovel_id

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (imovel_id,))
    conn.close()

def test_rota_inicial(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json == {
        'nome': 'API Projeto Eficaz',
        'status': 'online',
        'endpoint_principal': '/imoveis',
    }

def test_listar_imoveis(client, imovel_teste):
    response = client.get('/imoveis')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(i['id'] == imovel_teste for i in response.json)

def test_obter_imovel_existente(client, imovel_teste):
    response = client.get(f'/imoveis/{imovel_teste}')
    assert response.status_code == 200
    assert response.json['cidade'] == 'Cidade Teste'


def test_obter_imovel_inexistente(client):
    response = client.get('/imoveis/999999999')
    assert response.status_code == 404

def test_buscar_por_tipo(client, imovel_teste):
    response = client.get('/imoveis/tipo/casa')
    assert response.status_code == 200
    assert any(i['id'] == imovel_teste for i in response.json)

def test_buscar_por_cidade(client, imovel_teste):
    response = client.get(f'/imoveis/cidade/{quote("Cidade Teste")}')
    assert response.status_code == 200
    assert any(i['id'] == imovel_teste for i in response.json)

def test_criar_imovel(client):
    novo = {
        'logradouro': 'Avenida Nova',
        'tipo_logradouro': 'Avenida',
        'bairro': 'Bairro Novo',
        'cidade': 'Cidade Nova',
        'cep': '11111-111',
        'tipo': 'apartamento',
        'valor': 250000.0,
        'data_aquisicao': '2024-05-10',
    }
    response = client.post('/imoveis', json=novo)
    assert response.status_code == 201
    assert response.json['cidade'] == 'Cidade Nova'

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (response.json['id'],))
    conn.close()

def test_criar_imovel_sem_campos_obrigatorios(client):
    response = client.post('/imoveis', json={'tipo': 'casa'})
    assert response.status_code == 400

def test_atualizar_imovel(client, imovel_teste):
    response = client.put(f'/imoveis/{imovel_teste}', json={'valor': 350000.50})
    assert response.status_code == 200
    assert response.json['valor'] == pytest.approx(350000.50, rel=1e-4)

def test_atualizar_imovel_inexistente(client):
    response = client.put('/imoveis/999999999', json={'valor': 100.0})
    assert response.status_code == 404

def test_remover_imovel(client):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO imoveis (logradouro, cidade, tipo, valor) VALUES (%s, %s, %s, %s)",
            ('Rua Remover', 'Cidade Remover', 'terreno', 50000.0),
        )
        imovel_id = cursor.lastrowid
    conn.close()

    response = client.delete(f'/imoveis/{imovel_id}')
    assert response.status_code == 204

    response = client.get(f'/imoveis/{imovel_id}')
    assert response.status_code == 404

def test_remover_imovel_inexistente(client):
    response = client.delete('/imoveis/999999999')
    assert response.status_code == 404