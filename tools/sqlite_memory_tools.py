# tools/sqlite_memory_tools.py
from crewai.memory import Memory
from crewai.tools import tool

# ✅ Instância global de memória semântica
memory = CrewMemory()

@tool("Set Current SQLite Database")
def set_current_db_tool(db_name: str) -> str:
    """
    Define o banco de dados SQLite ativo que será usado pelas outras Tools.

    Args:
        db_name (str): Nome do banco de dados (ex: 'devcrew.db').

    Returns:
        str: Mensagem confirmando o banco configurado.
    """
    try:
        if not db_name.endswith(".db"):
            db_name += ".db"

        memory.save("current_db", db_name)
        return f"✅ Banco de dados ativo configurado para '{db_name}'."
    except Exception as e:
        return f"⚠️ Erro ao configurar banco de dados: {e}"


@tool("Get Current SQLite Database")
def get_current_db_tool() -> str:
    """
    Retorna o banco de dados SQLite atualmente configurado como ativo.

    Returns:
        str: Nome do banco ativo.
    """
    try:
        db = memory.get("current_db")
        if not db:
            return "📦 Nenhum banco configurado. Use 'Set Current SQLite Database' para definir um."
        return f"📦 Banco de dados ativo: '{db}'."
    except Exception as e:
        return f"⚠️ Erro ao obter banco de dados ativo: {e}"


def get_active_db_name() -> str:
    """
    Função auxiliar para uso interno por outras Tools.
    Retorna apenas o nome do banco atual ou 'devcrew.db' por padrão.
    """
    db = memory.get("current_db")
    if not db:
        db = "devcrew.db"
        memory.save("current_db", db)
    return db
