import sqlite3
import json
from crewai.tools import tool

@tool("SQLite Query Executor")
def execute_sqlite_query(db_name: str, sql: str) -> str:
    """
    Executa uma consulta SQL (SELECT) em um banco SQLite e retorna os resultados formatados.

    ⚠️ Apenas instruções de leitura são permitidas (SELECT, PRAGMA, etc.).

    Args:
        db_name (str): Nome do arquivo do banco (ex: 'devcrew.db').
        sql (str): Instrução SQL a ser executada. Exemplo: 'SELECT * FROM users;'

    Returns:
        str: Resultado formatado (em tabela ou JSON) ou mensagem de erro.
    """
    try:
        # Verificações básicas
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"

        sql_lower = sql.strip().lower()
        if not sql_lower.startswith(("select", "pragma", "explain")):
            return "🚫 Somente comandos de leitura são permitidos (SELECT, PRAGMA, EXPLAIN)."

        # Conecta ao banco
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Executa a query
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Se não houver resultados
        if not rows:
            conn.close()
            return "📭 Nenhum resultado encontrado."

        # Pega nomes das colunas
        columns = [desc[0] for desc in cursor.description]

        # Formata como JSON para melhor leitura no chat
        data = [dict(zip(columns, row)) for row in rows]
        pretty_json = json.dumps(data, ensure_ascii=False, indent=2, default=str)

        conn.close()
        return f"📊 Resultado da consulta:\n\n{pretty_json}"

    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
