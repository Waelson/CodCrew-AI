# tools/sqlite_execute_ddl_tool.py
import sqlite3
import re
from typing import Optional
from crewai.tools import tool

_ALLOWED_DDL_PREFIXES = (
    "create",
    "alter",
    "create index",
    "create unique index",
    "create trigger",
    "create view",
    "create table",
)

# palavras proibidas por padrão (operações destrutivas)
_PROHIBITED_KEYWORDS = ("drop", "delete", "truncate", "replace into")

@tool("SQLite Execute DDL")
def execute_sqlite_ddl(db_name: str, ddl_sql: str, force: Optional[bool] = False) -> str:
    """
    Executa instruções DDL em um banco SQLite.

    Args:
        db_name (str): nome do arquivo do banco (ex: 'devcrew.db')
        ddl_sql (str): script DDL a ser executado (pode conter múltiplas instruções; ex: 'CREATE TABLE ...;')
        force (bool, optional): se True permite palavras proibidas (DROP/DELETE/TRUNCATE) — usar com cautela.

    Retorna:
        str: mensagem de sucesso ou descrição do erro.
    ---
    Observações de segurança:
    - Por padrão, instruções contendo palavras potencialmente destrutivas (DROP/DELETE/TRUNCATE/REPLACE INTO)
      serão rejeitadas e a execução será abortada.
    - Se realmente desejar executar uma instrução destrutiva, passe force=True explicitamente.
    """
    try:
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"

        if not ddl_sql or not isinstance(ddl_sql, str):
            return "⚠️ O parâmetro 'ddl_sql' está vazio ou inválido."

        ddl_clean = ddl_sql.strip().lower()

        # Rejeita instruções obviamente não-DDL (ex: SELECT, INSERT) — aceitar apenas DDL-like
        # Aceitamos PRAGMA também, pois é comum no gerenciamento de esquema.
        if not any(ddl_clean.startswith(p) for p in _ALLOWED_DDL_PREFIXES) and not ddl_clean.startswith("pragma"):
            # permitir múltiplas instruções que começam com CREATE/ALTER/PRAGMA -- caso contrário, rejeitar
            # checar se contém CREATE/ALTER em algum ponto (para scripts multilinha)
            if not re.search(r"\b(create|alter|pragma)\b", ddl_clean):
                return "🚫 Apenas instruções DDL (CREATE/ALTER/PRAGMA/etc.) são permitidas por esta tool."

        # Bloqueio de palavras proibidas, a menos que force=True
        if not force:
            for bad in _PROHIBITED_KEYWORDS:
                if re.search(rf"\b{re.escape(bad)}\b", ddl_clean):
                    return (
                        f"🚫 A instrução contém a palavra proibida '{bad}'. "
                        "Operações destrutivas não são permitidas por padrão. "
                        "Use force=True apenas se tiver certeza do que está fazendo."
                    )

        # Executa o script com executescript (permite múltiplas instruções)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            cursor.executescript(ddl_sql)
            conn.commit()
        except sqlite3.OperationalError as oe:
            conn.rollback()
            conn.close()
            return f"⚠️ Erro operacional ao executar DDL: {oe}"
        except sqlite3.DatabaseError as de:
            conn.rollback()
            conn.close()
            return f"⚠️ Erro de banco ao executar DDL: {de}"

        conn.close()
        return f"✅ DDL executado com sucesso no banco '{db_name}'."
    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
