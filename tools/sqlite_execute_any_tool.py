import sqlite3
import json
from crewai.tools import tool

@tool("SQLite Execute Any SQL")
def execute_any_sql(db_name: str = None, sql: str = "") -> str:
    """
    Executa qualquer instrução SQL em um banco SQLite.
    Suporta SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, etc.

    Args:
        db_name (str): Nome do banco de dados (ex: 'devcrew.db'). Se não informado, usa o banco ativo.
        sql (str): Instrução SQL completa.

    Returns:
        str: Resultado formatado ou mensagem de sucesso.
    """
    try:
        if not sql or not isinstance(sql, str):
            return "⚠️ A instrução SQL está vazia ou inválida."


        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        sql_clean = sql.strip().lower()

        # Verifica se é uma consulta (SELECT)
        is_select = sql_clean.startswith("select") or sql_clean.startswith("pragma") or sql_clean.startswith("explain")

        if is_select:
            cursor.execute(sql)
            rows = cursor.fetchall()

            if not rows:
                conn.close()
                return "📭 Nenhum resultado encontrado."

            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, r)) for r in rows]
            pretty = json.dumps(data, indent=2, ensure_ascii=False, default=str)

            conn.close()
            return f"📊 Resultado da consulta:\n\n{pretty}"

        # Para outras instruções (INSERT, UPDATE, DELETE, CREATE, etc.)
        try:
            cursor.executescript(sql)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return f"⚠️ Erro ao executar SQL: {e}"

        affected = cursor.rowcount
        conn.close()

        return f"✅ Instrução executada com sucesso no banco '{db_name}'. Linhas afetadas: {affected if affected >= 0 else 'N/A'}"

    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
