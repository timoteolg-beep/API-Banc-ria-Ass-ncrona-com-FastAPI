import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configurações de chaves
# Dica: Em produção, isso viria de um arquivo .env
CHAVE_SECRETA = os.getenv("SECRET_KEY", "minha-chave-secreta-desafio-fastapi")
ALGORITMO = "HS256"
TEMPO_EXPIRACAO_MINUTOS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(senha: str):
    """Criptografa a senha antes de salvar no banco."""
    return pwd_context.hash(senha)

def verificar_senha(senha_pura, senha_hash):
    """Compara a senha digitada com o hash salvo."""
    return pwd_context.verify(senha_pura, senha_hash)

def criar_token_jwt(dados: dict):
    """Gera o 'crachá' (token) de acesso com validade de tempo."""
    dados_copia = dados.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=TEMPO_EXPIRACAO_MINUTOS)
    dados_copia.update({"exp": expiracao})
    
    token_codificado = jwt.encode(dados_copia, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado

def decodificar_token(token: str):
    """Lê o token e devolve os dados (ou erro se for inválido)."""
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        return payload.get("sub")
    except JWTError:
        return None
