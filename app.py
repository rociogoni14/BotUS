import streamlit as st

import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms.openai import OpenAI
import streamlit.components.v1 as components
import pandas as pd
#from openai import OpenAI




#Establezco mi clave de OpenAi
#api_key = st.secrets.openai_key
#Mientras no se desplieuge, se hace así
openai.api_key = "sk-proj-oV20eey4vj5RHAquDeaoT3BlbkFJriKbP68j0UF9sQYuZpTs"

#Diccionario con preguntas frecuentes
dicc_preg  = {
    "Investigadores":{"color":"#FFB6C1", 
                      "preguntas":[
        "¿Qué características hay que detallar en los contratos?",
        "¿Cuál es el plazo máximo para realizar la propuesta de adjudicación?",
        "Quiero saber la tabla de categorías de contratación.",
        "¿Cómo debe iniciar un investigador la tramitación de la convocatoria de seleción y futura contratación indefinida?",
        "¿Dónde puedo encontrar información relativa a cómo cumplimentar los campos de una oferta de contrato?",
        "¿Qué documentos hay que entregar para iniciar el proceso de contratación por parte del investigador?"

    ]
    },
    "Candidatos":{"color":"#FFD700", 
                  "preguntas": [
        "¿Dónde se publican las listas provisionales de admitidos?",
        "¿Cuáles son los requisitos para poder solicitar un contrato temporal?",
        "¿Cuál es el plazo de presentación de solicitudes para los contratos temporales?",
        "¿Cuáles el plazo máximo para formular reclamaciones?",
        "¿Qué documentación hay que aportar en la solicitud de un contrato?",
        "¿Con cuánta antelación se publica la convocatoria de la entrevista? ¿Dónde se publica?",
        "¿Dónde se registran las reclamaciones?",
        "¿Cuáles son los nombres de los proyectos ofertados en el mes de [mes]?",
        "¿Cuál es la información relativa a contratos ofertados para la titulación de [titulación] en el mes de [mes]?",
        "¿Cuál es el calendario de publicación de convocatorias de [año]?",
        "¿Cuál es el inicio y el fin del plazo de presentación de solicitudes para cada mes en [año]?",
        "¿Cuáles son las instrucciones para la presentación de solicitudes como candidato?"

    ]
    },
    "Ambos":{"color": "#AFEEEE", 
             "preguntas": [
        "¿Cuál es el procedimiento de contratación?",
        "¿Cuáles son los criterios de valoración de un candidato?",
        "Dentro de los criterios de valoración, ¿cómo puntúa cada uno?",
        "Cuáles son los criterios de desempate para los candidatos?",
        "¿Cuál es el proceso completo para contratar a un candidato?",
        "¿Dónde se firman los documentos?"

    ]
    }
}
if "opcion" not in st.session_state:
    st.session_state.opcion = None


title_container = st.container()
col1,col2 = st.columns([1,20])
with col1:
    image = st.image("US.png",width = 110)
with col2:

    st.markdown("<h1 style='text-align: center; color: #bd1353;'>BotUS Investigación</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #bd1353;'>Tu asistente personalizado del área de investigación de la Universidad de Sevilla!</h3>",
             unsafe_allow_html=True)

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
    st.session_state.historial = [{
        'role':'assistant', 
        'content': 'Estoy aquí para ayudarte a resolver tus dudas sobre los contratos de investigación de la Universidad de Sevilla. ¡No dudes en preguntarme lo que necesites!'
        }] #Lista de diccionarios que almacena el contenido y el rol
if "modelo" not in st.session_state:
    st.session_state.modelo = "gpt-3.5-turbo"
if "temperatura" not in st.session_state:
    st.session_state.temperatura = 0.0
if "index" not in st.session_state:
    st.session_state.index = None
if "init" not in st.session_state:
    st.session_state.init = False


def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error al leer el archivo de prompt: {e}")
        return ""

def load_data():
    with st.spinner(text = 
                    "Se está procesando toda la información relevante relacionada con los contratos del personal de investigación de la Universidad de Sevilla. En unos minutos podrá usar el chatbot"
                    ):
        lectura_ficheros = SimpleDirectoryReader(input_dir ="./data_md", recursive = True)
        docs = lectura_ficheros.load_data()
        ajustes = ServiceContext.from_defaults(llm=OpenAI(model=st.session_state.modelo, temperature=st.session_state.temperatura, system_prompt=prompt_init))
        index = VectorStoreIndex.from_documents(docs, service_context=ajustes)
        st.session_state.index =  index
        if "chat_engine" not in st.session_state.keys(): 
            st.session_state.chat_engine = st.session_state.index.as_chat_engine(chat_mode="react", verbose=True)

prompt_file_path = "prompt\prompt_mejorado.txt"

prompt_init = load_prompt(prompt_file_path)

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #ededed ;
    }
</style>
""", unsafe_allow_html=True)


def response_generator(prompt):
    response = st.session_state.chat_engine.chat(prompt)
    return response.response

def escribir_input():
    seleccion = [clave for clave,valor in st.session_state.items() if pd.api.types.is_bool(valor) and valor and clave!="init"]
    #st.write("seleccion", seleccion)
    #st.write("tipo de seleccion", type(seleccion))
    st.session_state.historial.append({'role': 'user', 'content': seleccion[0]})
    response = response_generator(seleccion[0])
    st.session_state.historial.append({'role':"assistant", 'content': response})
    
    

def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
    
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
       """
    components.html(f"{htmlstr}", height=1, width=1)

def creacion_botones(opcion,color):
    boton = st.button(opcion, key = opcion, on_click=escribir_input, help = opcion)
    ChangeButtonColour(opcion,'black',color)
    return boton


with st.sidebar:
    st.session_state.modelo = st.selectbox("Elige qué LLM quieres usar", ("gpt-3.5-turbo","gpt-3.5-turbo-instruct","gpt-4-turbo"))
    st.session_state.temperatura = st.slider("Elige la temperatura de tu modelo", min_value=0.0, max_value=1.0, value=0.5, step = 0.01)
    st.button("Aceptar", on_click=load_data)
    st.markdown("<h1 style='text-align: center; color: #bd1353;'>Preguntas frecuentes</h1>", unsafe_allow_html=True)
    contenedores = {}
    for clave in dicc_preg.keys():
        contenedores[clave] = st.container()
        color = dicc_preg[clave]['color']
        with contenedores[clave]:
            st.markdown("<h2 style='text-align: center; color: #bd1353;'>{}</h2>".format(clave), unsafe_allow_html=True)
            for opcion in dicc_preg[clave]['preguntas']:
                boton = creacion_botones(opcion,color)


if not st.session_state.init:
    load_data()
    st.session_state.init = True
        

for el in st.session_state.historial:
    with st.chat_message(el['role'], avatar = logo_dicc[el['role']]):
        st.write(el['content'])




prompt = st.chat_input("Introduzca la pregunta que quiera hacerle al asistente")

if prompt:
    st.session_state.historial.append({'role':"user", 'content': prompt})
    with st.chat_message('user', avatar = "avatar.png"):
        st.write(prompt)
    
    response = response_generator(prompt)
    st.session_state.historial.append({'role':"assistant", 'content': response})
    with st.chat_message('assistant', avatar = "US.png"):
        with st.spinner("Estoy buscando la información..."):
            st.write(response)
    
        

