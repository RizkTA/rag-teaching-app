import streamlit as st
import requests
import base64
import os

# =================================
# CONFIG
# =================================
API_URL = "https://rag-teaching-app.onrender.com"

UPLOAD_PASSWORD = os.getenv(
    "UPLOAD_PASSWORD",
    "supersecret123"
)

# =================================
# SESSION STATE
# =================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =================================
# PAGE CONFIG
# =================================
st.set_page_config(
    page_title="RIZK AI Assistant",
    page_icon="📕",
    layout="wide"
)

# =================================
# HEADER
# =================================
col1, col2 = st.columns([1, 6])

with col1:
    try:

        with open("RIZKRED.png", "rb") as f:

            data = base64.b64encode(
                f.read()
            ).decode()

        st.markdown(
            f"""
            <img src="data:image/png;base64,{data}" width="120">
            """,
            unsafe_allow_html=True
        )
    except:
        st.write("📕")

with col2:
    st.title(" 📕 RIZK AI Assistant")

    st.markdown(
        "       AI-powered Teaching Assistant "
    )

st.divider()

# =================================
# ASK QUESTIONS
# =================================
st.subheader("💬 Ask Questions")

query = st.text_input(
    "Ask a question:",
    placeholder="Example: What is data science?"
)

if st.button("🚀 Ask") and query.strip():

    with st.spinner("🧠...Thinking... 🧠"):

        try:
            res = requests.post(
                f"{API_URL}/query",
                json={"q": query},
                timeout=120
            )

            if res.status_code == 200:
                data = res.json()

                answer = data.get("answer", "No answer returned.")
                citations = data.get("citations", [])

                # SAVE CHAT
                st.session_state.messages.append({
                    "question": query,
                    "answer": answer
                })

                st.rerun()

            else:
                st.error(res.text)

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

# =================================
# CHAT HISTORY
# =================================
for msg in st.session_state.messages:
    st.markdown(f"### ❓ {msg['question']}")
    st.markdown("## 📘 Answer")
    st.write(msg[" answer"])

# =================================
# PDF UPLOAD
# =================================
st.divider()

st.subheader("📄 Upload PDF (Admin Only)")

password = st.text_input(
    "Enter upload password",
    type="password"
)

if password == UPLOAD_PASSWORD:

    uploaded_file = st.file_uploader("Choose PDF File", type=["pdf"])

    if uploaded_file and st.button("📥 Upload & Ingest"):

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
                    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                else:
                    st.error(res.text)

            except Exception as e:
              print("LLM ERROR:", e)
               
elif password:
    st.error("❌ Wrong password")

# =================================
# FOOTER
# =================================
st.divider()

st.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        padding:10px;
        font-size:16px;
        color:gray;
    ">
        <div style="
            font-size:28px;
            animation: floatBook 2s ease-in-out infinite;
        ">
            📖
        </div>

         Dr. Nouhad Rizk • AI Teaching Assistant

    </div>

    <style>
    @keyframes floatBook {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =================================
# SIDEBAR
# =================================
with st.sidebar:
    st.header("⚙️ Controls")

    # =========================
    # CLEAR CHAT
    # =========================
    if st.button(
            "🧹 Clear Chat",
            key="clear_chat_button"
    ):
        st.session_state.messages = []

        st.rerun()

    # =========================
    # BACK BUTTON
    # =========================
    if st.button(
            "⬅️ Back",
            key="back_button"
    ):

        if len(st.session_state.messages) > 0:
            st.session_state.messages.pop()

            st.rerun()

    st.markdown("---")

    # =========================
    # LOGO + TITLE
    # =========================
    try:

        with open("RIZKRED.png", "rb") as f:
            data = base64.b64encode(
                f.read()
            ).decode()

        st.markdown(
            """
            <div style="
                display:flex;
                flex-direction:column;
                justify-content:center;
                height:100%;
                padding-left:10px;
            ">

               📕📗📘📙📚📓📒📕📗📘📚
              <p> Dr. Nouhad Rizk </p>
              <p> Computer Science Department </p>
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.markdown("📘 RIZK AI Assistant")

