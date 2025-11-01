from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Task
from agents.planner import planner
from agents.researcher import researcher
from agents.coder import coder

def run_devcrew_task(user_input: str) -> str:
    """Executa o fluxo CrewAI e retorna uma string com o resultado."""
    task = Task(
        description=user_input,
        expected_output="Código Go e modelo de dados criado no SQLite.",
        agent=coder,  # agora o Coder é quem executa a ação
    )

    crew = Crew(
        agents=[planner, researcher, coder],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff(inputs={"prompt": user_input})

    # Retornar texto puro
    if hasattr(result, "raw"):
        return str(result.raw)
    elif hasattr(result, "output"):
        return str(result.output)
    else:
        return str(result)
