from crewai import Agent

researcher = Agent(
    role="Researcher Agent",
    goal="Buscar informações, bibliotecas, padrões e boas práticas relacionadas à tarefa.",
    backstory=(
        "Você é um pesquisador técnico detalhista, focado em encontrar "
        "as melhores soluções de engenharia disponíveis."
    ),
    verbose=True
)
