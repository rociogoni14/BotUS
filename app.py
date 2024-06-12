import streamlit as st
import random
import time
import openai
from llama_index.core import VectorStoreIndex, Settings, Document, SimpleDirectoryReader, ServiceContext
from llama_index.llms.openai import OpenAI
import os
from PyPDF2 import PdfReader
from streamlit_avatar import avatar
import base64
#from openai import OpenAI




#Establezco mi clave de OpenAi
#api_key = st.secrets.openai_key
#Mientras no se desplieuge, se hace así
openai.api_key = "sk-proj-oV20eey4vj5RHAquDeaoT3BlbkFJriKbP68j0UF9sQYuZpTs"
title_container = st.container()
col1,col2 = st.columns([1,20])
with col1:
    image = st.image("US.png",width = 110)
with col2:

    st.markdown("<h1 style='text-align: center; color: #bd1353;'>BotUS Investigación</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #bd1353;'>Tu asistente personalizado del área de investigación de la Universidad de Sevilla!</h3>", unsafe_allow_html=True)

st.logo("logo2_US.png", link = "https://investigacion.us.es/investigacion/contratos-personal/contratos-personal-hasta-mayo-2024")

st.html("""
  <style>
    [alt=Logo] {
      height: 4rem;
    }
  </style>
        """)

#Elegir icono en cuadro de diálogo
logo_dicc = {'user': 'avatar.png', 'assistant': 'US.png'}

if "historial" not in st.session_state:
    st.session_state.historial = [{'role':'assistant', 'content': 'Estoy aquí para ayudarte a resolver tus dudas sobre los contratos de investigación de la Universidad de Sevilla. ¡No dudes en preguntarme lo que necesites!'}] #Lista de diccionarios que almacena el contenido y el rol
if "modelo" not in st.session_state:
    st.session_state.modelo = "gpt-3.5-turbo"
if "temperatura" not in st.session_state:
    st.session_state.temperatura = 0.0
if "index" not in st.session_state:
    st.session_state.index = None

# Función para validar PDFs
def is_valid_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            if reader.is_encrypted:
                st.warning(f"El archivo {file_path} está encriptado y no se puede leer.")
                return False
            len(reader.pages)
        return True
    except Exception as e:
        st.error(f"Error al leer el archivo {file_path}: {e}")
        return False

def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error al leer el archivo de prompt: {e}")
        return ""
    
def load_data():
    with st.spinner(text = "Se está procesando toda la información relevante relacionada con los contratos del personal de investigación de la Universidad de Sevilla. En unos minutos podrá usar el chatbot"):
        #valid_files = []
        #for root, _, files in os.walk("./data"):
        #    for file in files:
        #        if file.lower().endswith('.pdf'):
        #            file_path = os.path.join(root, file)
        #            if is_valid_pdf(file_path):
        #                valid_files.append(file_path)
        
        #if not valid_files:
        #    st.error("No se encontraron archivos PDF válidos en la carpeta ./data.")
        #    return None
        
        
        
        lectura_ficheros = SimpleDirectoryReader(input_dir ="./data_md", recursive = True)
        docs = lectura_ficheros.load_data()
        ajustes = ServiceContext.from_defaults(llm=OpenAI(model=st.session_state.modelo, temperature=st.session_state.temperatura, system_prompt=prompt_init))
        index = VectorStoreIndex.from_documents(docs, service_context=ajustes)
        st.session_state.index =  index
        if "chat_engine" not in st.session_state.keys(): 
            st.session_state.chat_engine = st.session_state.index.as_chat_engine(chat_mode="react", verbose=True)

prompt_file_path = "prompt\prompt_mejorado.txt"
prompt_init = load_prompt(prompt_file_path)

#A8A7A7
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #ededed ;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.session_state.modelo = st.selectbox("Elige qué LLM quieres usar", ("gpt-3.5-turbo","gpt-3.5-turbo-instruct","gpt-4-turbo"))
    st.session_state.temperatura = st.slider("Elige la temperatura de tu modelo", min_value=0.0, max_value=1.0, value=0.5, step = 0.01)
    
    st.button("Aceptar", on_click=load_data)

#@st.cache_resource(show_spinner=False)

init = False
if not init:
    load_data()
    init = True
        

for el in st.session_state.historial:
    with st.chat_message(el['role'], avatar = logo_dicc[el['role']]):
        st.write(el['content'])


def response_generator():
    response = st.session_state.chat_engine.chat(prompt)
    return response.response

prompt = st.chat_input("Introduzca la pregunta que quiera hacerle al asistente")

if prompt:
    st.session_state.historial.append({'role':"user", 'content': prompt})
    with st.chat_message('user', avatar = "avatar.png"):
        st.write(prompt)
    
    response = response_generator()
    st.session_state.historial.append({'role':"assistant", 'content': response})
    with st.chat_message('assistant', avatar = "US.png"):
        with st.spinner("Estoy buscando la información..."):
            st.write(response)
    
        

