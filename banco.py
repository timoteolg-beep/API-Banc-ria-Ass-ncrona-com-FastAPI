from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

# Enum para garantir que só aceitamos esses dois tipos
class TipoTransacao(str, Enum):
    DEPOSITO = "deposito"
    SAQUE = "saque"

class BancoSimples:
    """
    Classe que simula um banco de dados em memória.
    Útil para testes locais sem precisar subir um container SQL.
    """
    def __init__(self):
        self.tabela_usuarios = {}
        self.tabela_transacoes = []

    def buscar_usuario(self, username: str):
        return self.tabela_usuarios.get(username)

    def salvar_novo_usuario(self, dados_usuario: dict):
        self.tabela_usuarios[dados_usuario["username"]] = dados_usuario

    def registrar_transacao(self, transacao: dict):
        self.tabela_transacoes.append(transacao)
        
        # Atualização atômica do saldo do cliente
        usuario = self.tabela_usuarios[transacao["user_id"]]
        if transacao["type"] == TipoTransacao.DEPOSITO:
            usuario["balance"] += transacao["amount"]
        else:
            usuario["balance"] -= transacao["amount"]

    def listar_transacoes_do_usuario(self, username: str):
        # Filtra apenas as transações do dono da conta
        return [t for t in self.tabela_transacoes if t["user_id"] == username]

# Instância global do banco para ser usada na aplicação
db = BancoSimples()
