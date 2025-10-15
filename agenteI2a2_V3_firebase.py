import os
import mimetypes
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from langchain_core.messages import HumanMessage

# =========================
# CONFIGURAÇÃO DO AMBIENTE
# =========================
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("Por favor, configure sua GROQ_API_kEY no .env ou no Streamlit secrets.")
    st.stop()

llm = ChatGroq(
    temperature=0,
    groq_api_key=groq_api_key,
    model_name='llama3-70b-8192'
)

# Inicialize o Firebase
if not firebase_admin._apps:
     # Substitua pelo caminho do seu arquivo de credenciais do Firebase
    cred = credentials.Certificate("CAMINHO_DO_ARQUIVO_DE_CONEXAO_COM_FIRE_BASE.json")
    firebase_admin.initialize_app(cred)
db_firestore = firestore.client()

def inserir_documento(tipo, conteudo):
    doc_ref = db_firestore.collection("documentos").document()
    doc_ref.set({
        "tipo": tipo,
        "conteudo": conteudo
    })

# =========================
# FUNÇÕES DE PROCESSAMENTO
# =========================

def processar_csv(file_path):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        inserir_documento("CSV", row.to_json())

def processar_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    inserir_documento("XML", ET.tostring(root, encoding='unicode'))

def processar_pdf_texto(file_path):
    reader = PdfReader(file_path)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    inserir_documento("PDF_TEXTO", texto)

def processar_pdf_imagem(file_path):
    imagens = convert_from_path(file_path)
    texto = ""
    for img in imagens:
        texto += pytesseract.image_to_string(img, lang="por")
    inserir_documento("PDF_IMAGEM", texto)

# =========================
# DETECÇÃO DO TIPO DE ARQUIVO
# =========================
def detectar_tipo_arquivo(file_path):
    tipo, _ = mimetypes.guess_type(file_path)
    if tipo == "text/csv":
        return "CSV"
    elif tipo == "application/xml" or file_path.lower().endswith(".xml"):
        return "XML"
    elif tipo == "application/pdf":
        # Detecta se é PDF texto ou imagem
        try:
            reader = PdfReader(file_path)
            if any(page.extract_text() for page in reader.pages):
                return "PDF_TEXTO"
            else:
                return "PDF_IMAGEM"
        except:
            return "PDF_IMAGEM"
    else:
        return "DESCONHECIDO"

# =========================
# INTERFACE STREAMLIT
# =========================
st.title("🧠 Agente Inteligente de Notas Fiscais")

uploaded_files = st.file_uploader(
    "Envie arquivos CSV, XML ou PDF:",
    type=["csv", "xml", "pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        tipo = detectar_tipo_arquivo(file_path)
        st.write(f"📄 Arquivo: {uploaded_file.name} — Detectado como **{tipo}**")

        if tipo == "CSV":
            processar_csv(file_path)
        elif tipo == "XML":
            processar_xml(file_path)
        elif tipo == "PDF_TEXTO":
            processar_pdf_texto(file_path)
        elif tipo == "PDF_IMAGEM":
            processar_pdf_imagem(file_path)
        else:
            st.warning("Tipo de arquivo não suportado.")

    st.success("Arquivos processados e salvos no Firestore.")

# =========================
# AGENTE DE CONSULTA FIRESTORE
# =========================
def consultar_documentos(pergunta):
    docs = db_firestore.collection("documentos").stream()
    dados = [doc.to_dict() for doc in docs]
    contexto = "Você é especialista em notas fiscais brasileiras. Responda em português com base nos dados abaixo:\n"
    for d in dados:
        contexto += f"\nTipo: {d['tipo']}\nConteúdo: {d['conteudo']}\n"
    contexto += f"\nPergunta: {pergunta}\n"
    try:
        resposta = llm([HumanMessage(content=contexto)])
        return resposta.content
    except Exception as e:
        st.error(f"Ocorreu um erro ao consultar o modelo Groq: {e}")
        return "O serviço Groq está indisponível no momento. Tente novamente mais tarde."

query = st.text_input("💬 Pergunte sobre os dados das notas fiscais:")

if query:
    with st.spinner("Consultando..."):
        resposta = consultar_documentos(query)
        st.write("📢 Resposta:", resposta)