from fastapi import APIRouter, HTTPException
from models.pedido import PedidoInput, PedidoOutput
from routers.pratos import pratos

router = APIRouter()
pedidos = []


@router.post("/", response_model=PedidoOutput, status_code=201)
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    if not prato["disponivel"]:
        raise HTTPException(status_code=400, detail=f"O prato '{prato['nome']}' não está disponível")

    preco_efetivo = prato["preco_promocional"] or prato["preco"]  # FIX: usa preço promocional
    novo_pedido = {
        "id": len(pedidos) + 1,
        "prato_id": pedido.prato_id,
        "nome_prato": prato["nome"],
        "quantidade": pedido.quantidade,
        "valor_total": preco_efetivo * pedido.quantidade,
        "observacao": pedido.observacao,
    }
    pedidos.append(novo_pedido)
    return novo_pedido


@router.get("/", response_model=list[PedidoOutput])
async def listar_pedidos():
    return pedidos


@router.get("/{pedido_id}", response_model=PedidoOutput)
async def buscar_pedido(pedido_id: int):
    for p in pedidos:
        if p["id"] == pedido_id:
            return p
    raise HTTPException(status_code=404, detail="Pedido não encontrado")
