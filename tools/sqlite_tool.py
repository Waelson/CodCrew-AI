import os
import sqlite3
from crewai.tools import tool  # ✅ novo sistema do CrewAI 1.x

@tool("SQLite Database Creator")
def create_sqlite_db_with_schema(db_name: str, schema_sql: str) -> str:
    """
    Cria automaticamente um banco SQLite com o nome e o script SQL fornecidos.

    Args:
        db_name (str): nome do arquivo do banco (ex: 'devcrew.db')
        schema_sql (str): script SQL de criação das tabelas

    Returns:
        str: mensagem de sucesso ou erro
    """
    try:
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"

        # 🚫 Evita comandos destrutivos
        if any(word in schema_sql.lower() for word in ["drop", "delete", "alter", "truncate"]):
            return "🚫 Operações destrutivas não são permitidas."

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()

        return f"✅ Banco '{db_name}' criado/atualizado com sucesso!"
    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
