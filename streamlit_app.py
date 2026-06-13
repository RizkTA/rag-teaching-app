import streamlit as st
import requests
import base64
import os


# =================================
# CONFIG
# =================================
API_URL = "https://rag-teaching-app.onrender.com"
#API_URL = "http://localhost:8000"

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
# ==============================
# ASK QUESTIONS (INPUT + BUTTON)
# ==============================
import time

st.subheader("💬 Chat with Rizk AI Assistant")

# =========================
# CHAT INPUT (ChatGPT STYLE)
# =========================
with st.form("chat_form", clear_on_submit=True):

    query = st.text_input("Ask a question...", key="chat_input")

    submitted = st.form_submit_button("🚀 Send")

if submitted and query.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.spinner("🧠 Thinking...🧠"):

        try:
            res = requests.post(
                f"{API_URL}/query",
                json={"q": query},
                timeout=120
            )

            # =========================
            # SAFE STATUS CHECK
            # =========================
            if res.status_code != 200:
                st.error("Backend error")
                st.code(res.text)
                st.stop()

            # =========================
            # SAFE JSON PARSE (ONLY ONCE)
            # =========================
            try:
                data = res.json()
            except Exception:
                st.error("Invalid JSON from backend")
                st.code(res.text)
                st.stop()

            answer = data.get("answer", "")

            # =========================
            # STREAMING EFFECT
            # =========================
            placeholder = st.empty()
            streamed = ""

            for word in answer.split():
                streamed += word + " "
                placeholder.markdown(streamed)
                time.sleep(0.02)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": data.get("sources", [])
            })

        except Exception as e:
            st.error(f"Request failed: {str(e)}")
            st.stop()
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

st.markdown("<div id='end'></div>", unsafe_allow_html=True)
st.markdown("<script>document.getElementById('end').scrollIntoView();</script>", unsafe_allow_html=True)
# =================================

# PDF UPLOAD
# =================================
st.divider()

# =========================
# INIT AUTH STATE SAFELY
# =========================
# =========================
# INIT AUTH STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.subheader("📄 Upload .pdf, .txt or .md (Admin Only)")

password = st.text_input(
    "Enter upload password",
    type="password",
    key="upload_password_unique_main"
)

if password:
    if password == UPLOAD_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.session_state.authenticated = False
        st.error("❌ Wrong password")

# =========================
# FILE UPLOAD SECTION
# =========================
if st.session_state.authenticated:

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "md", "txt"],
        key="file_uploader_mainn"
    )

    if uploaded_file:

        ext = uploaded_file.name.split(".")[-1].lower()

        progress_color = {
            "pdf": "#ff4b4b",
            "md": "#00c853",
            "txt": "#2196f3"
        }.get(ext, "#999999")

        file_icon = {
            "pdf": "📕",
            "md": "🟢",
            "txt": "🔵"
        }.get(ext, "📄")

        st.markdown(f"""
        <style>
        .stProgress > div > div > div > div {{
            background-color: {progress_color};
        }}
        </style>
        """, unsafe_allow_html=True)

        # =========================
        # SINGLE BUTTON ONLY (FIXED)
        # =========================

        if st.button("📥 Upload & Ingest"):

            progress = st.progress(0)

            try:

                st.write("🔥 Sending request...")

                progress.progress(20)

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                res = requests.post(
                    f"{API_URL}/upload_file",
                    files=files,
                    timeout=10
                )

                st.write("🔥 Request returned")

                progress.progress(80)

                st.write("STATUS:", res.status_code)

                st.write("TEXT:", res.text)

                progress.progress(100)

            except Exception as e:

                st.error(str(e))

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

         Dr. Nouhad Rizk • AI Knowledge Base
        
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

        try:
            st.markdown(
                """
                <div style="
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    height:100%;
                    padding-left:10px;
                ">

                  📕📗📘📙📚📓📒📕📗📘📚📕

                <div style="font-family: Arial, sans-serif; max-width: 400px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2 style="margin: 0 0 5px 0; color: #333;">Dr. Nouhad Rizk</h2>
                <div style="font-weight: bold; color: #555; margin-bottom: 2px;">Piper Professor &amp; Director of Undergraduate Studies</div>
                <div style="font-style: italic; color: #777; margin-bottom: 15px;">Computer Science Department</div>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 15px 0;">

                <div style="line-height: 1.6; color: #444;">
                    <div>📍 <strong>Address:</strong> 3551 Cullen Blvd, Houston, TX 77204</div>
                    <div>📞 <strong>Phone:</strong> <a href="tel:7137433710" style="color: #0066cc; text-decoration: none;">713-743-3710</a></div>
                    <div>🌐 <strong>Website:</strong> <a href="https://www.uh.edu/nouhadrizk" target="_blank" rel="noopener noreferrer" style="color: #0066cc; text-decoration: none;">uh.edu/nouhadrizk</a></div>
                </div>
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            st.markdown("📘 RIZK AI Assistant")
    except Exception:
        st.markdown("📘 RIZK AI Assistant")