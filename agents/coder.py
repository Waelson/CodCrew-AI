from crewai import Agent
from tools.sqlite_tool import create_sqlite_db_with_schema  # agora é uma função tool registrada

coder = Agent(
    role="Coder Agent",
    goal="Gerar código e modelos de dados em sql. Cria bancos SQLite automaticamente quando gerar schemas SQL.",
    backstory="Engenheiro especializado em Go e bancos relacionais.",
    tools=[create_sqlite_db_with_schema],  # ✅ passa a função decorada
    verbose=True
)
