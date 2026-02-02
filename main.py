import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from google.api_core.exceptions import ResourceExhausted
from utils.prompt import SYSTEM_PROMPT
from utils.text_config import ler_pdf, dividir_texto, buscar_contexto, efeito_digitando
from config.import_env import API_KEY




BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)



modelo = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=API_KEY
)





try:
    texto_pdf = ler_pdf("base/base.pdf")
    chunks_pdf = dividir_texto(texto_pdf) if texto_pdf else []
except FileNotFoundError:
    chunks_pdf = []
    




workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    response = modelo.invoke(state["messages"])
    return {"messages": response}

workflow.add_edge(START, "modelo")
workflow.add_node("modelo", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

def processar_mensagem(user_input: str) -> str:
    contexto = buscar_contexto(user_input, chunks_pdf)

    mensagens = [
        SystemMessage(content=f"""
{SYSTEM_PROMPT}

BASE DE CONHECIMENTO:
{contexto}
"""),
        HumanMessage(content=user_input)
    ]



    try:
        output = app.invoke({"messages": mensagens}, config=config)
        resposta = output["messages"][-1]
        return resposta.content

    except ResourceExhausted as e:
        #print("ERRO:", repr(e))
        return (
            "No momento estou com alto volume de solicitações. "
            "Por favor, tente novamente em alguns instantes."
        )

    except Exception as e:
        #print("ERRO:", repr(e))
        return "Ocorreu um erro ao processar sua solicitação."



#apenas para rodar no terminal

if __name__ == "__main__":
    print("Chat iniciado. Digite (SAIR) para encerrar.")

    while True:
        user_input = input("Você: ")

        if user_input.lower() == "sair":
            print("Encerrando Orion Agent...")
            break

        resposta = processar_mensagem(user_input)

        print("Orion IA: ", end="", flush=True)
        efeito_digitando(resposta)
