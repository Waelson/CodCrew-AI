from crewai import Agent
from tools.sqlite_tool import create_sqlite_db_with_schema  # agora é uma função tool registrada
from tools.sqlite_analyze_db_tool import analyze_sqlite_database
from tools.sqlite_query_tool import execute_sqlite_query
from tools.sqlite_execute_ddl_tool import execute_sqlite_ddl
from tools.sqlite_execute_any_tool import execute_any_sql


coder = Agent(
    role="Coder Agent",
    goal="Gerar código e modelos de dados em sql. Cria bancos SQLite automaticamente quando gerar schemas SQL.",
    backstory="Engenheiro sênior que cria e consulta bancos SQLite de forma segura",
    tools=[
        create_sqlite_db_with_schema, 
        analyze_sqlite_database, 
        execute_sqlite_query, 
        execute_sqlite_ddl,
        execute_any_sql
        ],  # ✅ passa a função decorada
    verbose=True
)
