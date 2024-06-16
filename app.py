import streamlit as st

import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms.openai import OpenAI
import streamlit.components.v1 as components
import pandas as pd




#Inicialización de la mayoría de variables de sesión
if "mes" not in st.session_state:
    st.session_state.mes = "[MES]"
if "año" not in st.session_state:
    st.session_state.año = "[AÑO]"
if "titulacion" not in st.session_state:
    st.session_state.titulacion = "[TITULACIÓN]"
if "historial" not in st.session_state:
    #Lista de diccionarios que almacena el contenido y el rol
    st.session_state.historial = [{
        'role':'assistant', 
        'content': 'Estoy aquí para ayudarte a resolver tus dudas sobre los contratos de investigación de la Universidad de Sevilla. ¡No dudes en preguntarme lo que necesites!'
        }] 
if "modelo" not in st.session_state:
    st.session_state.modelo = "gpt-3.5-turbo"
if "temperatura" not in st.session_state:
    st.session_state.temperatura = 0.0
if "index" not in st.session_state:
    st.session_state.index = None
if "init" not in st.session_state:
    st.session_state.init = False


#Diccionario con preguntas frecuentes. La clave del diccionario es la categoría de pregunta: Personalizable, Investigador o Candidato.
#su valor es otro diccionario con dos claves, color, que indica de qué color va a estar coloreado el botón de dicha pregunta, y preguntas
#que es una lista de todas las preguntas que pertenecen a esa categoría de pregunta. 
#En las preguntas personalizables, el valor que se muestra en la interfaz es el que configuren los usuarios
dicc_preg  = {
    "Personaliza tu pregunta!! ✒️":  {
        "color" : "#FFF8DC",
        "preguntas" : [
        "¿Cuáles son los nombres de los proyectos ofertados en el mes de {}?".format(st.session_state.mes),
        "¿Cuál es la información relativa a contratos ofertados para la titulación de {} en el mes de {}?".format(st.session_state.titulacion, st.session_state.mes),
        "¿Cuál es el calendario de publicación de convocatorias de {}?".format(st.session_state.año),
        "¿Cuál es el inicio y el fin del plazo de presentación de solicitudes para cada mes en {}?".format(st.session_state.año)

        ]
    },
    "Investigadores":{"color":"#FFEBCD", 
                      "preguntas":[
        "¿Qué características hay que detallar en los contratos?",
        "¿Cuál es el plazo máximo para realizar la propuesta de adjudicación?",
        "Quiero saber la tabla de categorías de contratación.",
        "¿Cómo debe iniciar un investigador la tramitación de la convocatoria de seleción y futura contratación indefinida?",
        "¿Dónde puedo encontrar información relativa a cómo cumplimentar los campos de una oferta de contrato?",
        "¿Qué documentos hay que entregar para iniciar el proceso de contratación por parte del investigador?"

    ]
    },
    "Candidatos":{"color":"#FFE4C6", 
                  "preguntas": [
        "¿Dónde se publican las listas provisionales de admitidos?",
        "¿Cuáles son los requisitos para poder solicitar un contrato temporal?",
        "¿Cuál es el plazo de presentación de solicitudes para los contratos temporales?",
        "¿Cuáles el plazo máximo para formular reclamaciones?",
        "¿Qué documentación hay que aportar en la solicitud de un contrato?",
        "¿Con cuánta antelación se publica la convocatoria de la entrevista? ¿Dónde se publica?",
        "¿Dónde se registran las reclamaciones?",
        "¿Cuáles son las instrucciones para la presentación de solicitudes como candidato?"

    ]
    },
    "Ambos":{"color": "#FFA07A", 
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

#Selecciono la lista de preguntas que es personalizable
botones_personales = dicc_preg["Personaliza tu pregunta!! ✒️"]["preguntas"]

#Creación del título centrado con el escudo de la Universidad de Sevilla a la izquierda
title_container = st.container()
col1,col2 = st.columns([1,20])
with col1:
    image = st.image("US.png",width = 110)
with col2:

    st.markdown("<h1 style='text-align: center; color: #bd1353;'>BotUS Investigación</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #bd1353;'>Tu asistente personalizado del área de investigación de la Universidad de Sevilla!</h3>",
             unsafe_allow_html=True)

#Definir un logo para la página
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



#Función para cargar el prompt
def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error al leer el archivo de prompt: {e}")
        return ""

#Función para leer todos los ficheros guardado en la carpeta data_md, guardarlos como documentos y vectorizarlos para que los use el modelo elegido por el usuario
#que de forma predeterminada está definido como gpt-3.5-turbo
def load_all_data():
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

#Se carga el prompt que se le va a mandar a la API de OpenAI
prompt_init = load_prompt(prompt_file_path)

#Se establaecen los estilos del sidebar
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #ededed ;
    }
</style>
""", unsafe_allow_html=True)

#Se le manda la pregunta hecha por el usuario al modelo y nos quedamos con su respuesta
def response_generator(prompt):
    response = st.session_state.chat_engine.chat(prompt)
    return response.response

#Guarda la pregunta hecha por el usuario a través de los botones en el historial y calcula su respuesta
def escribir_input():
    seleccion = [clave for clave,valor in st.session_state.items() if pd.api.types.is_bool(valor) and valor and clave!="init"]
    st.session_state.historial.append({'role': 'user', 'content': seleccion[0]})
    response = response_generator(seleccion[0])
    st.session_state.historial.append({'role':"assistant", 'content': response})
    
    
#Función que se utiliza para cambiarle el color a los botones
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

#Función para crear los botones de manera que al hacer click en ellos se llame a la función escribir_input explicada antes
def creacion_botones(opcion,color):
    boton = st.button(opcion, key = opcion, on_click=escribir_input, help = opcion)
    ChangeButtonColour(opcion,'black',color)
    return boton

#Función que permite que los cambios que se hagan en las preguntas personalizables se actualicen automáticamente
def actualizar_preguntas_personalizadas():
    dicc_preg["Personaliza tu pregunta!! ✒️"]["preguntas"] = [
        "¿Cuáles son los nombres de los proyectos ofertados en el mes de {}?".format(st.session_state.get('mes', '')),
        "¿Cuál es la información relativa a contratos ofertados para la titulación de {} en el mes de {}?".format(st.session_state.get('titulacion', ''), st.session_state.get('mes', '')),
        "¿Cuál es el calendario de publicación de convocatorias de {}?".format(st.session_state.get('año', '')),
        "¿Cuál es el inicio y el fin del plazo de presentación de solicitudes para cada mes en {}?".format(st.session_state.get('año', ''))
    ]

#Creación del sidebar
with st.sidebar:
    #Creación selectbox para elegir el modelo a usar
    st.session_state.modelo = st.selectbox("Elige qué LLM quieres usar", ("gpt-3.5-turbo","gpt-3.5-turbo-instruct","gpt-4-turbo"))
    #Creación de slider para seleccionar la temperatura del modelo
    st.session_state.temperatura = st.slider("Elige la temperatura de tu modelo", min_value=0.0, max_value=1.0, value=0.5, step = 0.01)
    #Creación de botón que hace que se actualicen estos cambios al hacer click en él
    st.button("Aceptar", on_click=load_all_data)
    st.markdown("<h1 style='text-align: center; color: #bd1353;'>Preguntas frecuentes (FAQs)</h1>", unsafe_allow_html=True)
    contenedores = {}
    for clave in dicc_preg.keys():
        contenedores[clave] = st.container()
        color = dicc_preg[clave]['color']
        if clave == "Personaliza tu pregunta!! ✒️":
            with contenedores[clave]:
                st.markdown("<h2 style='text-align: center; color: #bd1353;'>{}</h2>".format(clave), unsafe_allow_html=True)
                #Creación text_input para rellenar la titulación, su valor predeterminado es Ingeniería Informática
                st.session_state.titulacion = st.text_input("Introduce aquí el nombre de la titulación", value="Ingeniería Informática")
                col0,col1= st.columns(2)
                with col0:
                    #Creación de selectobox para elegir el mes
                    st.session_state.mes = st.selectbox("Selecciona el mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
                with col1:
                    #Creación de selectbox para elegir el año
                    st.session_state.año = st.selectbox("Elige el año", ["2023","2024"])

                #LLamada a la función que actualiza las preguntas personalizadas por el valor elegir por el usuario
                actualizar_preguntas_personalizadas()

                #Una vez actualizados los valores, se crean los botones
                for opcion in dicc_preg[clave]['preguntas']:
                    boton = creacion_botones(opcion,color)


        else:
            with contenedores[clave]:
                st.markdown("<h2 style='text-align: center; color: #bd1353;'>{}</h2>".format(clave), unsafe_allow_html=True)
                for opcion in dicc_preg[clave]['preguntas']:
                    boton = creacion_botones(opcion,color)

#Con esto se cargan todos los ficheros al principio del todo y luego ya, salvo que se carge un nuevo modelo, no se vuelve a ejecutar la función
if not st.session_state.init:
    load_all_data()
    st.session_state.init = True
        
#Se escribe en el chat_message el historial de preguntas y respuestas que está guardado en una variable de sesión
for el in st.session_state.historial:
    with st.chat_message(el['role'], avatar = logo_dicc[el['role']]):
        st.write(el['content'])



#Creación de un chay_input para que el usuario introduzca la pregunta
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
    
        

