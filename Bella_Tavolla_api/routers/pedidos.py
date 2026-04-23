from fastapi import APIRouter, HTTPException
from models.pedido import PedidoInput, PedidoOutput
from routers.pratos import pratos
import httpx # Necessário para chamar a API do Hugging Face

router = APIRouter()
pedidos = []

# Mock ou chamada real para o modelo do Hugging Face
import httpx
import os

# Função realista de consumo de API de ML
async def obter_preco_preditivo(prato_id: int):
    """
    Consome o Inference Endpoint do Hugging Face.
    """
    hf_api_url = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/seu-usuario/seu-modelo")
    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        return None # Falha segura se o token não existir (ex: rodando local sem .env)

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": {"prato_id": prato_id}}

    try:
        # Usa o httpx para fazer a requisição HTTP assíncrona
        async with httpx.AsyncClient() as client:
            response = await client.post(hf_api_url, headers=headers, json=payload, timeout=3.0)
            
            if response.status_code == 200:
                resultado = response.json()
                return resultado.get("preco_sugerido")
            return None
    except Exception:
        # Retorna None em caso de timeout ou queda do Hugging Face (Fallback)
        return None

@router.post("/", response_model=PedidoOutput, status_code=201)
async def criar_pedido(pedido: PedidoInput):
    # Localiza o prato usando gerador para eficiência (Caderno 03)
    prato = next((p for p in pratos if p["id"] == pedido.prato_id), None)
    
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    if not prato["disponivel"]:
        raise HTTPException(status_code=400, detail=f"O prato '{prato['nome']}' não está disponível")

    # INTEGRAÇÃO MLOps DEFINITIVA:
    # Tenta obter o preço da inferência do modelo; se falhar/não houver, usa o preço promocional ou base.
    preco_ia = await obter_preco_preditivo(pedido.prato_id)
    preco_efetivo = preco_ia or prato["preco_promocional"] or prato["preco"]

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