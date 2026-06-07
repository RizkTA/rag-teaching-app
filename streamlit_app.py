import streamlit as st
import requests
import base64
import os


# =================================
# CONFIG
# =================================
API_URL = "https://rag-teaching-app.onrender.com"

UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD", "")


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
# DISPLAY CHAT HISTORY
# =================================
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =================================
# CHAT INPUT
# =================================
query = st.chat_input("Ask a question")


# =================================
# ASK QUESTION
# =================================
if query:

    # save user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):

        with st.spinner("Thinking... 🧠"):

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
                        "No answer returned."
                    )

                    st.markdown(answer)

                    # save assistant response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    # citations
                    citations = data.get("citations", [])

                    if citations:

                        st.markdown("### 📚 Sources")

                        for c in citations:

                            source = c.get("source", "unknown")
                            score = round(c.get("score", 0), 3)

                            st.write(
                                f"- {source} (score: {score})"
                            )

                else:

                    try:
                        error_data = res.json()

                        st.error(
                            error_data.get(
                                "error",
                                "Unknown backend error"
                            )
                        )

                    except:
                        st.error(res.text)

            except Exception as e:

                st.error(
                    f"Connection Error: {str(e)}"
                )


# =================================
# PDF UPLOAD
# =================================
st.divider()

st.subheader("📄 Upload PDF (Admin Only)")

password = st.text_input(
    "Enter upload password",
    type="password"
)

if password and password == UPLOAD_PASSWORD:

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("🚀 Upload & Ingest"):

            with st.spinner(
                "Uploading and ingesting PDF..."
            ):

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

                        st.success(
                            "✅ PDF uploaded successfully"
                        )

                        st.json(res.json())

                    else:

                        try:
                            st.error(res.json())

                        except:
                            st.error(res.text)

                except Exception as e:

                    st.error(str(e))

elif password:

    st.warning("Wrong password ❌")


# =================================
# SIDEBAR
# =================================
with st.sidebar:

    st.header("⚙️ Controls")

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    try:

        with open("RIZKRED.png", "rb") as f:

            data = base64.b64encode(
                f.read()
            ).decode()

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