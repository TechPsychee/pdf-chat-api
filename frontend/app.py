import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://localhost:8000/v1"
API_KEY = os.getenv("API_KEY", "my-secure-api-key")


def upload_pdf():
    st.header("PDF Upload")

    uploaded_file = st.file_uploader(
        "Choose a PDF file", type=["pdf"], key="pdf_uploader"
    )

    if uploaded_file is not None:
        if st.button("Upload", key="upload_button"):
            with st.spinner("Uploading..."):
                files = {"file": uploaded_file}
                headers = {"X-API-Key": API_KEY}

                try:
                    response = requests.post(
                        f"{API_URL}/pdf", headers=headers, files=files
                    )

                    if response.status_code == 200:
                        pdf_info = response.json()
                        st.success("Upload successful!")
                        st.session_state["pdf_id"] = pdf_info["pdf_id"]
                        st.session_state["pdf_info"] = pdf_info
                        st.json(pdf_info)
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def chat_with_pdf():
    st.header("Chat with PDF")

    if "pdf_id" not in st.session_state:
        st.warning("Please upload a PDF first")
        return

    pdf_id = st.session_state["pdf_id"]

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat history
    for i, message in enumerate(st.session_state["messages"]):
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    with st.form("chat_form"):
        user_input = st.text_input(
            "Your question:",
            placeholder="Ask me about the content of the PDF...",
            key="chat_input",
        )
        submit_button = st.form_submit_button("Send", use_container_width=True)

        if submit_button and user_input:
            # Add user message to history
            st.session_state["messages"].append({"role": "user", "content": user_input})

            # Get AI response
            headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

            try:
                response = requests.post(
                    f"{API_URL}/chat/{pdf_id}",
                    headers=headers,
                    json={"message": user_input},
                )

                if response.status_code == 200:
                    ai_response = response.json()["response"]
                    # Add AI response to history
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": ai_response}
                    )
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Clear chat button (outside the form)
    if st.button("Clear Chat History", key="clear_button"):
        st.session_state["messages"] = []
        st.rerun()


def main():
    st.set_page_config(page_title="PDF Chat App", page_icon="📄", layout="wide")

    st.title("PDF Chat Application")

    # Add tabs
    tab1, tab2 = st.tabs(["Upload PDF", "Chat"])

    with tab1:
        upload_pdf()

    with tab2:
        chat_with_pdf()

    # Add sidebar with info
    with st.sidebar:
        st.header("Information")
        if "pdf_info" in st.session_state:
            st.write(f"Filename: {st.session_state['pdf_info'].get('filename', 'N/A')}")
            st.write(f"Pages: {st.session_state['pdf_info'].get('pages', 'N/A')}")
            st.write(f"Size: {st.session_state['pdf_info'].get('size', 'N/A')} bytes")
            st.write(
                f"Text chunks: {st.session_state['pdf_info'].get('chunk_count', 'N/A')}"
            )


if __name__ == "__main__":
    main()
