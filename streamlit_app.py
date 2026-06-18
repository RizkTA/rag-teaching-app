import streamlit as st
import requests
import base64
import os
import time
import re
from datetime import datetime

# =================================
# CONFIG
# =================================

API_URL = "https://rag-teaching-app.onrender.com"
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD", "supersecret123")


# =================================
# SESSION STATE
# =================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pinned" not in st.session_state:
    st.session_state.pinned = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "favorites" not in st.session_state:
    st.session_state.favorites = []
# =================================
# CSS
# =================================
st.markdown("""
<style>
.user-bubble {
    background: #E8F0FE;
    padding: 14px;
    border-radius: 12px;
    margin: 8px 0;
    border-left: 3px solid #4CAF50;
}

.bot-bubble {
    background: #FFFFE0;
    padding: 14px;
    border-radius: 12px;
    margin: 8px 0;
    border-left: 3px solid #4CAF50;
}

.pin-card {
    background: #F5F5F5;
    border-left: 5px solid #FFD700;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.pinned-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}

.favorite-star {
    color: gold;
    font-size: 22px;
}
</style>
""", unsafe_allow_html=True)

# =================================
# PAGE CONFIG
# =================================
st.set_page_config(page_title="RIZK AI", page_icon="📕", layout="wide")

# =================================
# HEADER
# =================================
col1, col2 = st.columns([1, 6])

with col1:
    try:
        with open("RIZKRED.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"<img src='data:image/png;base64,{data}' width='120'>", unsafe_allow_html=True)
    except:
        st.write("📕")

with col2:
    st.title("📕 RIZK AI Assistant")
    st.markdown("AI-powered Teaching Assistant")

st.divider()

# =================================
# LOTTIE ICON
# =================================
def load_lottie(url):
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

lottie_bulb = load_lottie("https://assets10.lottiefiles.com/packages/lf20_6wutsrox.json")

# =================================
# CHAT INPUT
# =================================
st.subheader("💬 Chat with RIZK AI")

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])

    with col1:
        query = st.text_input("Ask a question...", label_visibility="collapsed")

    with col2:
        submitted = st.form_submit_button("➤")

# =================================
# CALL BACKEND
# =================================
if submitted and query.strip():

    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("🧠 Thinking..."):

        try:
            res = requests.post(
                f"{API_URL}/query",
                json={"q": query},
                timeout=120
            )

            if res.status_code != 200:
                st.error("Backend error")
                st.code(res.text)
                st.stop()

            data = res.json()

            print("BACKEND RESPONSE:", data)

            answer = data.get("answer", "")
            st.write(data)
            print("ANSWER:", answer)
            print("ANSWER LENGTH:", len(answer))
            print(answer[:1000])
            sources = data.get("sources", [])

            print("SOURCE COUNT:", len(sources))


            # CLEAN
            answer = re.sub(r"dlab\d+_\d+", "", answer).strip()

            # STREAM
            placeholder = st.empty()
            streamed = ""

            for word in answer.split():
                streamed += word + " "
                placeholder.markdown(streamed)
                time.sleep(0.02)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": sources
            })

        except Exception as e:
            st.error(str(e))

    st.rerun()
# =================================
# PINNED NOTEBOOK V2
# =================================
if st.session_state.pinned:

    st.markdown("## 📚 AI Study Notebook")

    # =========================
    # SEARCH
    # =========================
    search_pin = st.text_input(
        "🔍 Search pinned notes"
    )

    # =========================
    # EXPORT
    # =========================
    export_text = ""

    for p in st.session_state.pinned:
        export_text += (
            f"QUESTION:\n{p['question']}\n\n"
            f"ANSWER:\n{p['answer']}\n\n"
            f"{'-'*50}\n"
        )

    st.download_button(
        "📥 Export Notes",
        export_text,
        file_name="rizk_ai_notes.txt"
    )

    # =========================
    # DELETE ALL
    # =========================
    if st.button("🗑 Clear All Notes"):

        st.session_state.pinned = []
        st.rerun()

    st.markdown("---")

    st.markdown(
        "<div class='pinned-container'>",
        unsafe_allow_html=True
    )

    for idx, pin in enumerate(st.session_state.pinned):

        # search filter
        if search_pin:

            if (
                search_pin.lower()
                not in pin["question"].lower()
                and
                search_pin.lower()
                not in pin["answer"].lower()
            ):
                continue

        favorite = pin.get("favorite", False)

        star = "⭐" if favorite else "☆"

        st.markdown(
            f"""
            <div class="pin-card">
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">

                    <b>💡 {pin['question']}</b>

                    <span class="favorite-star">
                        {star}
                    </span>

                </div>

                <br>

                {pin['answer']}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        # FAVORITE
        with col1:

            if st.button(
                "⭐ Favorite",
                key=f"fav_{idx}"
            ):

                st.session_state.pinned[idx]["favorite"] = (
                    not favorite
                )

                st.rerun()

        # UNPIN
        with col2:

            if st.button(
                "❌ Remove",
                key=f"remove_{idx}"
            ):

                st.session_state.pinned.pop(idx)

                st.rerun()

        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True )
    st.markdown()
st.write("MESSAGE COUNT:", len(st.session_state.messages))
if st.session_state.messages:
    st.write(st.session_state.messages[-1])
# =================================
# CHAT HISTORY (CLEAN)
# =================================
for i, msg in enumerate(st.session_state.messages):

    # USER
    if msg["role"] == "user":
  #      col1, col2 = st.columns([0.01, 10])  # almost no space for icon

   #     with col2:
            st.markdown(
                f"""
                <div class="user-bubble">
                    <b>💡You:</b><br><br>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

    # ASSISTANT
    else:
        # =================================
        # PIN BUTTON
        # =================================
        if st.button(
                "📌 Save to Notes (Press ⬅️ Back to export saved notes)",
                key=f"pin_{i}"
        ):

            previous_question = ""

            for j in range(i - 1, -1, -1):

                if st.session_state.messages[j]["role"] == "user":
                    previous_question = (
                        st.session_state.messages[j]["content"]
                    )

                    break

            # prevent duplicates
            already_exists = any(
                p["question"] == previous_question
                for p in st.session_state.pinned
            )

            if already_exists:

                st.warning("Already saved")

            else:

                st.session_state.pinned.append({
                    "question": previous_question,
                    "answer": msg["content"],
                    "favorite": False
                })

                st.success("Saved to notebook")
        st.markdown(f"""
        <div class="bot-bubble">
            <b>📘 RIZK AI Assistant:</b><br><br>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)

        citations = msg.get("citations", [])

        if citations:
           # best = max(citations, key=lambda x: x.get("score", 0))

            best = citations[0]


            with st.expander("📚 Sources"):

                st.markdown("**Best Source**")

                st.write(
                    f"• {best.get('source')} "
                    f"({round(best.get('score', 0), 3)})"
                )

                st.caption(
                    best.get("text", "")[:250]
                )

import os
import pandas as pd
from datetime import datetime

HISTORY_FILE = "upload_history.csv"


def load_history():

    if os.path.exists(HISTORY_FILE):

        try:
            return pd.read_csv(HISTORY_FILE)

        except Exception:
            pass

    return pd.DataFrame(
        columns=[
            "date",
            "time",
            "file",
            "type",
            "status"
        ]
    )


def save_history(df):

    df.to_csv(
        HISTORY_FILE,
        index=False
    )


def add_history(
    filename,
    filetype,
    status
):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo("America/Chicago"))



    history = load_history()

    new_row = pd.DataFrame([{
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "file": filename,
        "type": filetype,
        "status": status
    }])

    history = pd.concat(
        [history, new_row],
        ignore_index=True
    )

    save_history(history)

    st.session_state.upload_history = (
        history.to_dict("records")
    )
# =================================
# UPLOAD SECTION
# =================================
# ============================================
# 🚀 RIZK AI Upload System v3
# ============================================

import hashlib
import pandas as pd

# =================================
# SESSION STATE
# =================================
if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

# =================================
# HEADER
# =================================
st.divider()
st.subheader("📄 Upload Knowledge Files (Admin)")

password = st.text_input(
    "Enter upload password",
    type="password",
    key="upload_password"
)

if password:
    st.session_state.authenticated = (
        password == UPLOAD_PASSWORD
    )

# =================================
# FILE COLORS
# =================================
progress_color = {
    "pdf": "#ff4b4b",
    "md": "#00c853",
    "txt": "#2196f3"
}

file_icon = {
    "pdf": "📕",
    "md": "🟢",
    "txt": "🔵"
}

# =================================
# HASH FUNCTION
# =================================
def compute_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

# =================================
# MAIN UPLOAD UI
# =================================
if st.session_state.authenticated:

    uploaded_files = st.file_uploader(
        "Drag & Drop files here",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.markdown("### 📦 Files Ready")

        for file in uploaded_files:

            ext = file.name.split(".")[-1].lower()

            icon = file_icon.get(ext, "📄")

            st.info(f"{icon} {file.name}")

        # =================================
        # REPLACE OPTION
        # =================================
        replace_existing = st.checkbox(
            "♻ Replace existing files if duplicates found"
        )
        # =================================
        # UPLOAD BUTTON
        # =================================
        if st.button("🚀 Upload & Ingest All"):

            overall_progress = st.progress(0)

            total_files = len(uploaded_files)

            for idx, uploaded_file in enumerate(uploaded_files):

                ext = uploaded_file.name.split(".")[-1].lower()

                file_bytes = uploaded_file.getvalue()

                file_hash = compute_hash(file_bytes)

                with st.expander(f"📄 {uploaded_file.name}"):

                    st.write(f"Hash: `{file_hash}`")

                    progress = st.progress(5)

                    try:

                        files = {
                            "file": (
                                uploaded_file.name,
                                file_bytes,
                                "application/octet-stream"
                            )
                        }

                        data = {
                            "replace_existing": str(replace_existing),
                            "file_hash": file_hash
                        }

                        st.write(
                            "Calling URL:",
                            f"{API_URL}/upload_file"
                        )

                        progress.progress(25)

                        # =================================
                        # SINGLE REQUEST ONLY
                        # =================================
                        res = requests.post(
                            f"{API_URL}/upload_file",
                            files=files,
                            data=data,
                            timeout=300
                        )

                        progress.progress(50)

                        st.write(
                            "HTTP Status:",
                            res.status_code
                        )

                        st.code(res.text)

                        # =================================
                        # HTTP ERROR
                        # =================================
                        if res.status_code != 200:
                            st.error(
                                f"❌ Upload failed for {uploaded_file.name}"
                            )

                            add_history(
                                uploaded_file.name,
                                ext.upper(),
                                f"❌ HTTP {res.status_code}"
                            )

                            continue

                        # =================================
                        # PARSE JSON
                        # =================================
                        try:

                            result = res.json()

                        except Exception:

                            st.error(
                                "❌ Backend returned invalid JSON"
                            )

                            st.code(res.text)

                            add_history(
                                uploaded_file.name,
                                ext.upper(),
                                "❌ Invalid JSON"
                            )

                            continue

                        progress.progress(80)

                        status = result.get(
                            "status",
                            "unknown"
                        )

                        # =================================
                        # SKIPPED
                        # =================================
                        if status == "skipped":

                            st.warning(
                                f"⚠️ {uploaded_file.name} already exists"
                            )

                            add_history(
                                uploaded_file.name,
                                ext.upper(),
                                "⚠️ Skipped"
                            )

                        # =================================
                        # SUCCESS
                        # =================================
                        elif status in ["ok", "uploaded"]:

                            chunks = result.get(
                                "chunks",
                                0
                            )

                            st.success(
                                f"✅ {uploaded_file.name} uploaded successfully "
                                f"({chunks} chunks)"
                            )

                            add_history(
                                uploaded_file.name,
                                ext.upper(),
                                "✅ Uploaded"
                            )

                        # =================================
                        # BACKEND ERROR
                        # =================================
                        else:

                            st.error(
                                f"❌ Upload failed for {uploaded_file.name}"
                            )

                            st.json(result)

                            add_history(
                                uploaded_file.name,
                                ext.upper(),
                                "❌ Failed"
                            )

                        progress.progress(100)

                    except Exception as e:

                        st.error(
                            f"❌ Upload failed for {uploaded_file.name}"
                        )

                        st.code(str(e))

                        add_history(
                            uploaded_file.name,
                            ext.upper(),
                            "❌ Exception"
                        )

                overall_progress.progress(
                    int(
                        ((idx + 1) / total_files) * 100
                    )
                )

            # =================================
            # HISTORY
            # =================================
            history_df = load_history()

            if not history_df.empty:
                st.subheader("📜 Upload History")

                st.dataframe(
                    history_df.sort_values(
                        by=["date", "time"],
                        ascending=False
                    ),
                    width="stretch"
                )

                csv = history_df.to_csv(
                    index=False
                )

                st.download_button(
                    label="📥 Download Upload History",
                    data=csv,
                    file_name="upload_history.csv",
                    mime="text/csv"
                )

        # =================================
        # OVERALL PROGRESS
        # =================================
        #overall_progress.progress(
        #         int(((idx + 1) / total_files) * 100)  )


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
