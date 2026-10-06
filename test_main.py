from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_caminho_feliz_criacao_e_pagamento_pedido():
    payload = {
        "unidade_id": "REC-01",
        "canal": "APP",
        "itens": [
            {"produto_id": "P01", "nome": "Cuscuz Recheado", "quantidade": 2, "preco_unitario": 12.50},
            {"produto_id": "P02", "nome": "Café Passado", "quantidade": 1, "preco_unitario": 5.00}
        ],
        "cpf_cliente": "12345678900",
        "aceitou_lgpd": True
    }
    
    response_criar = client.post("/api/v1/pedidos", json=payload)
    assert response_criar.status_code == 201
    dados_pedido = response_criar.json()
    
    assert dados_pedido["valor_total"] == 30.00
    assert dados_pedido["pontos_fidelidade"] == 30
    assert dados_pedido["status"] == "PENDENTE"
    
    pedido_id = dados_pedido["pedido_id"]
    
    response_pagamento = client.post(f"/api/v1/pedidos/{pedido_id}/confirmar-pagamento")
    assert response_pagamento.status_code == 200
    assert response_pagamento.json()["status"] == "PAGO"