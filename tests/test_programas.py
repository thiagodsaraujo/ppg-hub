# tests/test_programas_api.py
from __future__ import annotations
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cria_lista_programa() -> None:
    payload = {"instituicao_id": 1, "nome": "Programa de Pós-Graduação em Ciências Farmacêuticas", "sigla": "PPGCF", "nivel": "Mestrado"}
    r = client.post("/programas", json=payload)
    assert r.status_code == 201, r.text
    r2 = client.get("/programas")
    assert r2.status_code == 200
    assert any(p["sigla"] == "PPGCF" for p in r2.json())
