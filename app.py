import streamlit as st
from api import get_response

st.title("DOJO BOT 🤖")
knowledge= "La fundacion comunidad DOJO es una organizacion" \
"no gubernamental sin fines de lucro que busca cambiar vidas" \
"a traves de la formacion en ciberseguridad" \
"lo hacen a traves de programas de impacto para jovenes y adultos." 


# hacemos historial de chat para hacerlo mas real jajaja
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("En que puedo ayudarte?"):
    
    st.session_state.messages.append({"role":"user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = get_response(context="", prompt=prompt)()
        response = st.write_stream(stream)
    st.session_state.messages.append({"role":"assistant", "content": response})
