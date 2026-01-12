from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from banco import TipoTransacao # Importando do nosso arquivo local

# --- Modelos de Entrada (O que o usuário manda) ---

class DadosCadastro(BaseModel):
    username: str
    password: str
    full_name: str

class PedidoTransacao(BaseModel):
    type: TipoTransacao
    # Validamos para garantir que ninguém deposite valor negativo ou zero
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Valor da operação (maior que zero)")

# --- Modelos de Saída (O que a API responde) ---

class RespostaUsuario(BaseModel):
    username: str
    full_name: str
    balance: Decimal

class RespostaToken(BaseModel):
    access_token: str
    token_type: str

class DetalheTransacao(BaseModel):
    id: str
    type: TipoTransacao
    amount: Decimal
    timestamp: datetime

class ExtratoCompleto(BaseModel):
    account_owner: str
    current_balance: Decimal
    transactions: list[DetalheTransacao]
