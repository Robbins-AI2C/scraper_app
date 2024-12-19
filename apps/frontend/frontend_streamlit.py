import streamlit as st
import requests


st.title("Scrape Google Maps (Experimental)")

user_input = st.text_input("Search for: ")

if st.button("Submit"):
    # Send data to FastAPI backend
    response = requests.post("http://localhost:8000/process", json={"data": user_input})
    if response.status_code == 200:
        st.success(f"Result: {response.json()['result']}")
    else:
        st.error("Something went wrong!")
