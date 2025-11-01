from crewai import Task

build_api_task = Task(
    description=(
        "Crie um serviço REST em Go que possua um endpoint de login "
        "recebendo usuário e senha, e retorne um token JWT válido."
    ),
    expected_output="Código Go funcional e plano de execução detalhado.",
    agent=None  # será definido no main
)
