import re
import gradio as gr
from main import run_devcrew_task

def clean_markdown(text: str) -> str:
    """Garante que blocos de código e markdown sejam válidos para o Chatbot."""
    if not text:
        return "⚠️ Sem resposta dos agentes."

    # Remove caracteres ou blocos incompletos
    text = text.strip()

    # Se houver um bloco aberto sem fechamento ```
    if text.count("```") % 2 != 0:
        text += "\n```"

    # Substitui triplo crase malformado por markdown padrão
    text = re.sub(r"```(\w+)?", "```\\1\n", text)
    return text

def chat_interface(user_input, history):
    """Executa a CrewAI e retorna resposta formatada ao Chatbot."""
    try:
        response = run_devcrew_task(user_input)
        clean_response = clean_markdown(response)
        history.append((user_input, clean_response))
    except Exception as e:
        history.append((user_input, f"⚠️ Erro: {str(e)}"))
    return "", history

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 DevCrew AI — Seu time de agentes de desenvolvimento")
    chatbot = gr.Chatbot(label="DevCrew Chat", render_markdown=True)
    msg = gr.Textbox(
        placeholder="Descreva a tarefa (ex: 'gerar API em Go com JWT')",
        label="Envie uma instrução para seus agentes"
    )

    msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])

demo.launch()
