from crewai import Crew, Task
from agents.coder import coder

def run_devcrew_task(user_input: str) -> str:
    """
    Executa o fluxo principal do DevCrew-AI.
    Permite gerar código em Golang e interagir com bancos SQLite.
    """
    # Detecta tipo de intenção (simples, mas eficaz)
    lower_input = user_input.lower()
    if any(x in lower_input for x in ["create table", "insert into", "select", "sqlite", "banco", "tabela", "usuário", "users"]):
        expected = "Interação com o banco SQLite: criação, inserção ou listagem de dados."
    elif any(x in lower_input for x in ["golang", "go code", "package main", "func main", "api", "endpoint", "struct"]):
        expected = "Geração de código em Golang conforme solicitado."
    else:
        expected = "Ação relacionada a código ou banco de dados."

    # Define a task dinâmica
    task = Task(
        description=user_input,
        expected_output=expected,
        agent=coder,
    )

    # Executa o Crew
    crew = Crew(agents=[coder], tasks=[task], verbose=True)
    result = crew.kickoff(inputs={"prompt": user_input})

    # Normaliza o retorno
    if hasattr(result, "raw"):
        return str(result.raw)
    elif hasattr(result, "output"):
        return str(result.output)
    else:
        return str(result)
