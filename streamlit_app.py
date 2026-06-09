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

if "pinned" not in st.session_state:
    st.session_state.pinned = []

# =================================
# CUSTOM CSS
# =================================
st.markdown("""
<style>
/* USER MESSAGE */
.user-bubble {
    background-color: #E8F0FE;
    color: black;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    border-left: 5px solid #4285F4;
}

/* AI MESSAGE */
.bot-bubble {
    background-color: #FFF8E1;
    color: black;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    border-left: 5px solid #F4B400;
}

/* PINNED CARD */
.pin-card {
    background: #F5F5F5;
    color: black;
    border-left: 5px solid #FFD700;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* FOOTER */
.footer {
    text-align:center;
    padding-top:20px;
    color:gray;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

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

# =================================
# ASK QUESTIONS
# =================================
st.subheader("💬 Ask Questions")

query = st.text_input(
    "Ask a question:",
    placeholder="Example: What is data science?"
)

# =================================
# ASK BUTTON
# =================================
if st.button("🚀 Ask"):

    if not query.strip():

        st.warning("Please enter a question.")

    else:

        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": query
        })

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

                    citations = data.get(
                        "citations",
                        []
                    )

                    # Store assistant answer
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations
                    })

                else:

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Backend Error: {res.text}",
                        "citations": []
                    })

            except Exception as e:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Connection Error: {str(e)}",
                    "citations": []
                })

# =================================
# PINNED ANSWERS
# =================================
if st.session_state.pinned:

    st.markdown("## 📌 Pinned Answers")

    for pin in st.session_state.pinned:
        st.markdown(
            f"""
            <div class="pin-card">
                <b>❓ {pin['question']}</b><br><br>
                📘 {pin['answer']}
            </div>
            """,
            unsafe_allow_html=True
        )
# =================================
# CHAT HISTORY
# =================================

# =================================
# CHAT HISTORY
# =================================
for i, msg in enumerate(st.session_state.messages):

    # =========================
    # USER MESSAGE
    # =========================
    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="user-bubble">
                <b>❓ You:</b><br><br>
                {msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # ASSISTANT MESSAGE
    # =========================
    else:

        st.markdown(
            f"""
            <div class="bot-bubble">
                <b>📘 RIZK AI Assistant:</b><br><br>
                {msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Sources
        citations = msg.get("citations", [])

        if citations:

            with st.expander("📚 Sources"):

                for c in citations:
                    source = c.get(
                        "source",
                        "unknown"
                    )

                    score = round(
                        c.get("score", 0),
                        3
                    )

                    st.write(
                        f"• {source} (score: {score})"
                    )

        # Buttons row
        col1, col2 = st.columns(2)

        # Pin button
        with col1:

            if st.button(
                    "📌 Pin",
                    key=f"pin_{i}"
            ):

                previous_question = ""

                # find previous user message
                for j in range(i - 1, -1, -1):

                    if st.session_state.messages[j]["role"] == "user":
                        previous_question = st.session_state.messages[j]["content"]
                        break

                st.session_state.pinned.append({
                    "question": previous_question,
                    "answer": msg["content"]
                })

                st.success("Pinned!")

        # Delete button
        with col2:

            if st.button(
                    "🗑 Delete",
                    key=f"delete_{i}"
            ):
                st.session_state.messages.pop(i)

                st.rerun()


# =================================
#st.markdown(f"### ❓ {msg['question']}")
#    st.markdown("## 📘 Answer")
#    st.write(msg[" answer"])
# PDF UPLOAD
# =================================
st.divider()

st.subheader("📄 Upload PDF (Admin Only)")

password = st.text_input(
    "Enter upload password",
    type="password"
)

if password == UPLOAD_PASSWORD:
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "md", "txt"]
    )

    if uploaded_file and st.button("📥 Upload & Ingest"):

        with st.spinner("Uploading and ingesting file..."):

            try:
                file_bytes = uploaded_file.getvalue()

                # detect type
                filename = uploaded_file.name
                ext = filename.split(".")[-1].lower()

                mime_map = {
                    "pdf": "application/pdf",
                    "md": "text/markdown",
                    "txt": "text/plain"
                }

                res = requests.post(
                    f"{API_URL}/upload_file",  # ✅ IMPORTANT FIX
                    files={
                        "file": (
                            filename,
                            file_bytes,
                            mime_map.get(ext, "application/octet-stream")
                        )
                    },
                    timeout=300
                )

                if res.status_code == 200:

                    st.success(f"✅ {filename} uploaded & ingested successfully!")

                    st.json(res.json())

                else:
                    st.error(res.text)

            except Exception as e:
                st.error(str(e))

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
              <p>Piper Professor</p>
              <p>Director of Undergraduate Studies</p>
              <p>3551 Cullen Blvd</p>
              <p>Houston, Tx 77204</p>
              <p>Phone: 713-743-3710</p>
              <p><a href="URL">https://www.uh.edu/nouhadrizk</a></p>
              </p>

            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.markdown("📘 RIZK AI Assistant")