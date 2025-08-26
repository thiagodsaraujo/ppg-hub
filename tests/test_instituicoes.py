from __future__ import annotations
from uuid import uuid4
from fastapi.testclient import TestClient

# OBS: o TestClient e o get_db já vêm do conftest (fixture `client`)
# from app.main import app
# client = TestClient(app)

def ensure_instituicao(client: TestClient, payload: dict) -> dict:
    """
    Tenta criar a instituição. Se já existir (409), busca por código e retorna a existente.
    Esse padrão torna o teste idempotente para rodar quantas vezes quiser (populate).
    """
    r = client.post("/instituicoes", json=payload)
    if r.status_code in (200, 201):
        return r.json()
    if r.status_code == 409:
        # Já existe -> busca por código
        codigo = payload["codigo"]
        r2 = client.get(f"/instituicoes?codigo={codigo}")
        assert r2.status_code == 200, f"Falha ao buscar '{codigo}' após 409"
        items = r2.json().get("items", [])
        assert items, f"Conflito ao criar '{codigo}', mas não encontrado via busca"
        return items[0]
    raise AssertionError(f"Falha ao criar instituição: {r.status_code} {r.text}")


def test_create_and_get_instituicao(client: TestClient):
    """
    Caso de teste usando código FIXO ('UEPB'): idempotente (create-or-get).
    Roda múltiplas vezes sem quebrar e sempre garante que a instância existe no banco.
    """
    payload = {
        "codigo": "UEPB",
        "nome_completo": "Universidade Estadual da Paraíba",
        "nome_abreviado": "UEPB",
        "sigla": "UEPB",
        "tipo": "Estadual",
        "cnpj": "12.345.678/0001-90",
        "endereco": {"logradouro": "Rua Baraúnas, 351", "cidade": "Campina Grande", "uf": "PB"},
        "contatos": {"email_principal": "contato@uepb.edu.br"},
        "website": "https://uepb.edu.br",
        "ativo": True,
    }

    obj = ensure_instituicao(client, payload)
    _id = obj["id"]

    # Garante leitura por ID
    r2 = client.get(f"/instituicoes/{_id}")
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["id"] == _id
    assert body2["codigo"] == payload["codigo"]


def test_seed_instituicoes_bulk(client: TestClient):
    """
    Exemplo para semear várias instituições com códigos ÚNICOS (evita 409).
    Útil quando você quer popular o banco com muitos registros.
    """
    bases = ["UFCG", "IFPB", "UFPE", "UFRN"]
    for base in bases:
        codigo = f"{base}_{uuid4().hex[:6].upper()}"
        payload = {
            "codigo": codigo,
            "nome_completo": f"{base} - Universidade Exemplo",
            "nome_abreviado": codigo,
            "sigla": codigo[:10],
            "tipo": "Federal" if base != "UEPB" else "Estadual",
            "ativo": True,
        }
        obj = ensure_instituicao(client, payload)
        assert obj["codigo"] == codigo
