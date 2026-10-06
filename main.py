from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import uuid

app = FastAPI(
    title="API Raízes do Nordeste",
    description="Sistema de gestão de pedidos para a rede Raízes do Nordeste",
    version="1.0.0"
)

class CanalVenda(str, Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"

class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"

class ItemPedido(BaseModel):
    produto_id: str
    nome: str
    quantidade: int = Field(..., gt=0)
    preco_unitario: float = Field(..., gt=0)

class CriarPedidoDTO(BaseModel):
    unidade_id: str
    canal: CanalVenda
    itens: List[ItemPedido]
    cpf_cliente: Optional[str] = None
    aceitou_lgpd: bool = False

class PedidoResponse(BaseModel):
    pedido_id: str
    unidade_id: str
    canal: CanalVenda
    valor_total: float
    pontos_fidelidade: int
    status: StatusPedido

banco_pedidos = {}

@app.post("/api/v1/pedidos", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(dto: CriarPedidoDTO):
    if not dto.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter ao menos um item.")
    
    total = sum(item.quantidade * item.preco_unitario for item in dto.itens)
    
    pontos = 0
    if dto.cpf_cliente and dto.aceitou_lgpd:
        pontos = int(total)
    
    pedido_id = str(uuid.uuid4())[:8]
    
    novo_pedido = {
        "pedido_id": pedido_id,
        "unidade_id": dto.unidade_id,
        "canal": dto.canal,
        "valor_total": total,
        "pontos_fidelidade": pontos,
        "status": StatusPedido.PENDENTE
    }
    
    banco_pedidos[pedido_id] = novo_pedido
    return novo_pedido

@app.post("/api/v1/pedidos/{pedido_id}/confirmar-pagamento", response_model=PedidoResponse)
def confirmar_pagamento(pedido_id: str):
    pedido = banco_pedidos.get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    pedido["status"] = StatusPedido.PAGO
    return pedido