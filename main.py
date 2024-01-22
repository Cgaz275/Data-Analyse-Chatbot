import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px


st.title("Chat Bot")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []

file_data = ""

file_read = st.file_uploader("")
if file_read is not None:
    file = pd.read_csv(file_read)
    file_data = file.to_string()
    st.write(file)
    num_rows, num_column = file.shape
    if num_column == 1:
        display_data = px.bar(file, x=file.columns[0], title='')
    elif num_column >= 2:
        display_data = px.line(file, x=file.columns[1], y=file.columns[2],
                               title="This is line chart for area " + file.columns[0] + " after years")
    st.plotly_chart(display_data)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Input here..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": f"searching on data : " + file_data + "and answer question from user : " + prompt + ". If there aren't any question related to data, you don't need to base on it, just answer base on what you know"
        }
    )

    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        full_response = ""
        holder = st.empty()

        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            holder.markdown(full_response + "_")
            holder.markdown(full_response)
        holder.markdown(full_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )
