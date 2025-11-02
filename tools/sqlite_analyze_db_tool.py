import sqlite3
from crewai.tools import tool

@tool("SQLite Analyze Database")
def analyze_sqlite_database(db_name: str) -> str:
    """
    Analisa todas as tabelas existentes em um banco SQLite, listando:
    - Nome da tabela
    - Número de colunas
    - Nomes e tipos das colunas
    - Número de registros em cada tabela

    Args:
        db_name (str): Nome do arquivo do banco de dados (ex: 'devcrew.db')

    Returns:
        str: Relatório detalhado da estrutura do banco.
    """
    try:
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Obtém todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            conn.close()
            return f"⚠️ Nenhuma tabela encontrada no banco '{db_name}'."

        report = [f"🧩 Análise do banco: **{db_name}**\n"]

        for (table_name,) in tables:
            # Estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            # Contagem de registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            (row_count,) = cursor.fetchone()

            report.append(f"### 🗂️ Tabela: `{table_name}`")
            report.append(f"- Registros: **{row_count}**")
            report.append(f"- Colunas ({len(columns)}):")

            for col in columns:
                cid, name, ctype, notnull, dflt_value, pk = col
                pk_flag = " (PK)" if pk else ""
                report.append(f"  • `{name}` — {ctype or 'TEXT'}{pk_flag}")

            report.append("")  # linha em branco

        conn.close()

        return "\n".join(report)

    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
