import sqlite3
import json
from typing import Any, Dict, Iterable, List, Tuple, Union
from crewai.tools import tool

JsonLike = Union[Dict[str, Any], str]

@tool("SQLite Generic Inserter")
def insert_into_table(db_name: str, table_name: str, record: JsonLike, return_row: bool = False) -> str:
    """
    Insere um registro na tabela especificada de um banco SQLite, de forma genérica.

    Args:
        db_name (str): nome do arquivo do banco (ex: 'devcrew.db').
        table_name (str): nome da tabela onde será inserido o registro.
        record (dict | str): dicionário contendo {coluna: valor} ou JSON string.
        return_row (bool): se True, busca e retorna a linha inserida (quando possível).

    Retorna:
        str: mensagem de sucesso com id inserido ou descrição do erro.
    """
    try:
        # Normalizações simples
        if not db_name.endswith(".db"):
            db_name = f"{db_name}.db"
        table_name = table_name.strip()

        # Parse record se veio como JSON string
        if isinstance(record, str):
            try:
                record_dict = json.loads(record)
            except json.JSONDecodeError:
                return "⚠️ O parâmetro 'record' é string não-JSON. Passe JSON válido ou um dicionário."
        elif isinstance(record, dict):
            record_dict = record
        else:
            return "⚠️ O parâmetro 'record' deve ser um dict ou um JSON string representando um objeto."

        if not record_dict:
            return "⚠️ O registro fornecido está vazio."

        # Conectar ao banco
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            conn.close()
            return f"⚠️ A tabela '{table_name}' não existe no banco '{db_name}'."

        # Obter metadados da tabela
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols_info: List[Tuple] = cursor.fetchall()
        if not cols_info:
            conn.close()
            return f"⚠️ Não foi possível obter a estrutura da tabela '{table_name}'."

        # cols_info: [(cid, name, type, notnull, dflt_value, pk), ...]
        column_names: List[str] = [col[1] for col in cols_info]

        # Validar campos fornecidos vs colunas da tabela
        provided_cols = set(record_dict.keys())
        allowed_cols = set(column_names)

        invalid_cols = provided_cols - allowed_cols
        if invalid_cols:
            return f"⚠️ As colunas {sorted(list(invalid_cols))} não existem na tabela '{table_name}'. Colunas válidas: {sorted(column_names)}"

        # Build insert: only provided columns (let database apply defaults for others)
        insert_cols = [c for c in column_names if c in record_dict]
        if not insert_cols:
            return "⚠️ Nenhuma coluna válida fornecida para inserção."

        placeholders = ", ".join(["?"] * len(insert_cols))
        cols_sql = ", ".join([f'"{c}"' for c in insert_cols])  # escape simples com aspas duplas
        values = [record_dict[c] for c in insert_cols]

        # Executa inserção de forma parametrizada
        try:
            cursor.execute(f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders});", tuple(values))
            conn.commit()
        except sqlite3.IntegrityError as ie:
            conn.rollback()
            conn.close()
            return f"⚠️ Violação de integridade: {ie}"
        except sqlite3.OperationalError as oe:
            conn.rollback()
            conn.close()
            return f"⚠️ Erro operacional ao inserir: {oe}"

        last_row_id = cursor.lastrowid

        # Opcional: retornar a linha inserida (se solicitado)
        if return_row:
            # Tenta buscar por ROWID ou pela PK caso exista
            # Se last_row_id == 0, pode não haver rowid (p.ex. tabela WITHOUT ROWID), então buscar por combinação de valores
            fetched: List[Tuple] = []
            try:
                if last_row_id and last_row_id != 0:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE rowid = ? LIMIT 1;", (last_row_id,))
                    fetched = cursor.fetchall()
                if not fetched:
                    # tenta localizar pela combinação dos valores fornecidos
                    where_clauses = " AND ".join([f'"{c}" = ?' for c in insert_cols])
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {where_clauses} LIMIT 1;", tuple(values))
                    fetched = cursor.fetchall()
            except Exception:
                fetched = []

            # Formata a linha
            if fetched:
                # pega nomes das colunas na ordem do cursor.description
                col_names = [d[0] for d in cursor.description] if cursor.description else column_names
                row = fetched[0]
                row_dict = {col_names[i]: row[i] for i in range(len(row))}
                conn.close()
                pretty = json.dumps(row_dict, default=str, ensure_ascii=False, indent=2)
                return f"✅ Inserido com sucesso (rowid={last_row_id}).\nLinha:\n{pretty}"

        conn.close()
        return f"✅ Inserido com sucesso (rowid={last_row_id})."

    except sqlite3.Error as e:
        return f"⚠️ Erro SQLite: {e}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"
