import streamlit as st
from api import get_response

st.title("IT Support Assistant 🖥️")

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
        stream = get_response(prompt, "data/soporte_data.txt")()
        response = st.write_stream(stream)
    st.session_state.messages.append({"role":"assistant", "content": response})
