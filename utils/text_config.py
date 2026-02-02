from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time
import os
import os
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ler_pdf(nome_arquivo):
    caminho_pdf = os.path.join(BASE_DIR, "..", nome_arquivo)

    if not os.path.exists(caminho_pdf):
        return None

    try:
        reader = PdfReader(caminho_pdf)
        texto = ""

        for page in reader.pages:
            texto += page.extract_text() + "\n"

        return texto

    except Exception as e:
        print(f"[AVISO] Erro ao ler PDF: {e}")
        return None


def dividir_texto(texto):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_text(texto)


def buscar_contexto(pergunta, chunks):
    if not chunks:
        return None

    pergunta_lower = pergunta.lower()
    relevantes = []

    for chunk in chunks:
        if any(p in chunk.lower() for p in pergunta_lower.split()):
            relevantes.append(chunk)

    return "\n".join(relevantes[:3]) if relevantes else None




def efeito_digitando(texto, atraso=0.02):
    for char in texto:
        print(char, end='', flush=True)
        time.sleep(atraso)
    print()