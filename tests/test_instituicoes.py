from __future__ import annotations
from fastapi import status


def test_create_and_get_instituicao(client):
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
        "ativo": True
    }
    r = client.post("/instituicoes", json=payload)
    assert r.status_code == status.HTTP_201_CREATED, r.text
    data = r.json()
    assert data["id"] > 0
    assert data["codigo"] == "UEPB"
    assert data["endereco_completo"].startswith("Rua Baraúnas, 351")

    _id = data["id"]
    r2 = client.get(f"/instituicoes/{_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == _id


def test_unique_codigo_sigla_conflict(client):
    payload = {
        "codigo": "UFCG",
        "nome_completo": "Universidade Federal de Campina Grande",
        "nome_abreviado": "UFCG",
        "sigla": "UFCG",
        "tipo": "Federal"
    }
    r1 = client.post("/instituicoes", json=payload)
    assert r1.status_code == 201
    # Confere conflito por código
    payload2 = dict(payload)
    payload2["sigla"] = "UFCG2"
    r2 = client.post("/instituicoes", json=payload2)
    assert r2.status_code == 409
    # Confere conflito por sigla
    payload3 = dict(payload)
    payload3["codigo"] = "UFCG2"
    r3 = client.post("/instituicoes", json=payload3)
    assert r3.status_code == 409


def test_list_pagination(client):
    client.post("/instituicoes", json={
        "codigo": "IFPB", "nome_completo": "Instituto Federal da Paraíba", "nome_abreviado": "IFPB", "sigla": "IFPB", "tipo": "Federal"
    })
    r = client.get("/instituicoes?limit=1&offset=0")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body
    assert body["limit"] == 1


def test_update_and_404(client):
    r = client.put("/instituicoes/9999", json={"nome_abreviado": "X"})
    assert r.status_code == 404

    # cria e atualiza
    r2 = client.post("/instituicoes", json={
        "codigo": "ESTADUALPB", "nome_completo": "Universidade Estadual PB", "nome_abreviado": "UEPB2", "sigla": "UEPB2", "tipo": "Estadual"
    })
    _id = r2.json()["id"]
    r3 = client.put(f"/instituicoes/{_id}", json={"nome_abreviado": "UEPB (Atualizada)"})
    assert r3.status_code == 200
    assert r3.json()["nome_abreviado"] == "UEPB (Atualizada)"


def test_validation_422(client):
    # Falta campos obrigatórios
    r = client.post("/instituicoes", json={"codigo": "X"})
    assert r.status_code == 422
