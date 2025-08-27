from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_404_problem_details():
    r = client.get("/instituicoes/999999")
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == 404
    assert body["title"] == "Instituição não encontrada" or "HTTP error" in body["title"]
    assert "instance" in body

def test_422_problem_details():
    # Supondo PATCH que espera dict em 'endereco' e você manda string
    r = client.patch("/instituicoes/1", json={"endereco": "não é json"})
    assert r.status_code == 422
    body = r.json()
    assert body["title"] == "Payload inválido"
    assert "errors" in body and "items" in body["errors"]

def test_409_integrity_problem_details(mocker):
    # Simule IntegrityError em commit do service para ver o 409
    from sqlalchemy.exc import IntegrityError
    mocker.patch(
        "app.services.instituicao_service.InstituicaoService._commit_or_raise",
        side_effect=IntegrityError("stmt", {}, Exception("Key (sigla)=(UEPB) already exists")),
    )
    r = client.put("/instituicoes/2", json={"nome_completo":"X","nome_abreviado":"X","sigla":"UEPB"})
    assert r.status_code == 409
    body = r.json()
    assert body["title"] == "Violação de integridade"
    assert body["status"] == 409
    assert "errors" in body
