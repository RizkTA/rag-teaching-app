import streamlit as st
import requests
import base64

#API_URL = "https://rag-teaching-app.onrender.com"
import os

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000"
)
#UPLOAD_PASSWORD = "supersecret123"
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")
# =================================
# PAGE CONFIG
# =================================
st.set_page_config(
    page_title="RIZK AI Assistant",
    page_icon="📕",
    layout="wide"
)

st.title("📕 RIZK AI Assistant")

# =================================
# SESSION STATE
# =================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =================================
# CHAT SECTION
# =================================
st.subheader("💬 Ask Questions")

query = st.text_input(
    "Ask a question:",
    key="query_input"
)

if st.button("Ask", key="ask_button") and query:

    with st.spinner("Thinking... 🧠🧠🧠"):

        try:

            res = requests.post(
                f"{API_URL}/query",
                json={"q": query},
                timeout=120
            )

            if res.status_code == 200:

                data = res.json()

                answer = data.get(
                    "answer",
                    "No answer returned"
                )

                st.markdown("### 📘 Answer")
                st.write(answer)

                # Optional sources
                sources = data.get("sources", [])

                if sources:

                    st.markdown("### 📚 Sources")

                    for s in sources:
                        st.write(f"- {s}")

            else:

                try:
                    error_data = res.json()
                    st.error(error_data.get("error", "Unknown error"))

                except:
                    st.error(res.text)

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

# =================================
# PDF UPLOAD
# =================================
st.divider()

st.subheader("📄 Upload PDF (Admin Only)")

password = st.text_input(
    "Enter upload password",
    type="password",
    key="upload_password"
)

if password == UPLOAD_PASSWORD:

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_file and st.button(
        "🚀 Upload & Ingest",
        key="upload_button"
    ):

        with st.spinner("Uploading and ingesting PDF..."):

            try:

                res = requests.post(
                    f"{API_URL}/upload_pdf",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=300
                )

                if res.status_code == 200:

                    st.success("✅ PDF uploaded successfully")

                    st.json(res.json())

                else:

                    try:
                        st.error(res.json())

                    except:
                        st.error(res.text)

            except Exception as e:
                st.error(str(e))

else:

    if password:
        st.warning("Wrong password ❌")

# =================================
# SIDEBAR
# =================================
with st.sidebar:

    st.header("⚙️ Controls")

    if st.button(
        "🧹 Clear Chat",
        key="clear_chat_button"
    ):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    try:

        with open("RIZKRED.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <div style="display:flex;align-items:center;">
                <img src="data:image/png;base64,{data}" width="90">
                <span style="margin-left:10px;">
                    Dr. Nouhad Rizk AI Teaching Assistant
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    except:
        pass
