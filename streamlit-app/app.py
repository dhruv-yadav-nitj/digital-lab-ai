import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

main_website = os.getenv('MAIN_WEBSITE_NAME')

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def get_manual_context(manual_id):
    response = requests.get(f"http://{main_website}/api/manual/{manual_id}")
    if response.status_code == 200:
        data = response.json()
        return "\n".join([
            f"Title: {data.get('title', '')}",
            f"Apparatus: {data.get('apparatus', '')}",
            f"Theory: {data.get('theory', '')}",
            f"Procedure: {data.get('procedures', '')}",
            f"Precautions: {data.get('precautions', '')}"
        ])
    else:
        return "Manual not found."


st.set_page_config(page_title="AI Lab Manual", layout="centered")
st.title("💬 AI Lab Assistant")

manual_id = st.query_params.get("id")

context = get_manual_context(manual_id)

user_input = st.text_input("Ask something about the manual:")


if st.button("Send") and user_input:
    messages = [
        {"role": "system", "content": f"You are a helpful assistant for lab manuals.\n\n{context}"},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    st.markdown(f"{reply}")
