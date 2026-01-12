from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Importando nossos módulos locais (A mágica da organização!)
from banco import db, TipoTransacao
from modelos import (
    DadosCadastro, RespostaUsuario, RespostaToken, 
    PedidoTransacao, DetalheTransacao, ExtratoCompleto
)
import seguranca

app = FastAPI(
    title="Desafio Bank API",
    description="API para gestão de contas correntes e transações financeiras.",
    version="2.0.0" # Versão atualizada
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Dependência de Autenticação ---
async def obter_usuario_logado(token: str = Depends(oauth2_scheme)):
    username = seguranca.decodificar_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    usuario = db.buscar_usuario(username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    return usuario

# --- Rotas da API ---

@app.post("/auth/registro", response_model=RespostaUsuario, status_code=201)
async def registrar_cliente(cliente: DadosCadastro):
    if db.buscar_usuario(cliente.username):
        raise HTTPException(status_code=400, detail="Ops! Esse nome de usuário já existe.")
    
    novo_usuario = {
        "username": cliente.username,
        "full_name": cliente.full_name,
        "hashed_password": seguranca.gerar_hash_senha(cliente.password),
        "balance": Decimal("0.00")
    }
    db.salvar_novo_usuario(novo_usuario)
    return novo_usuario

@app.post("/auth/login", response_model=RespostaToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = db.buscar_usuario(form_data.username)
    
    if not usuario or not seguranca.verificar_senha(form_data.password, usuario["hashed_password"]):
        raise HTTPException(status_code=400, detail="Login falhou. Verifique usuário e senha.")
    
    token = seguranca.criar_token_jwt(dados={"sub": usuario["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/transacoes", response_model=DetalheTransacao, status_code=201)
async def nova_transacao(
    pedido: PedidoTransacao, 
    usuario_atual: dict = Depends(obter_usuario_logado)
):
    # Regra de Ouro: Não deixar sacar mais do que tem
    if pedido.type == TipoTransacao.SAQUE:
        if usuario_atual["balance"] < pedido.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Transação negada. Saldo disponível: R$ {usuario_atual['balance']}"
            )

    transacao = {
        "id": str(uuid4()),
        "user_id": usuario_atual["username"],
        "type": pedido.type,
        "amount": pedido.amount,
        "timestamp": datetime.now(timezone.utc)
    }
    
    db.registrar_transacao(transacao)
    return transacao

@app.get("/meu-extrato", response_model=ExtratoCompleto)
async def ver_extrato(usuario_atual: dict = Depends(obter_usuario_logado)):
    transacoes = db.listar_transacoes_do_usuario(usuario_atual["username"])
    
    return {
        "account_owner": usuario_atual["full_name"],
        "current_balance": usuario_atual["balance"],
        "transactions": transacoes
    }
