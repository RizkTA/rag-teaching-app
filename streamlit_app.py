import requests
import os
import re
from app.history import load_history, save_history
import time
import random
import threading
from app.history import get_uploaded_files


API_URL = "https://learning-app-t2bz.onrender.com"
def upload_animation():

    st.markdown("""

<style>

@keyframes pulse {

0%{transform:scale(1);}
50%{transform:scale(1.18);}
100%{transform:scale(1);}

}

@keyframes books {

0%{
transform:translateX(-40px);
opacity:.2;
}

25%{
opacity:1;
}

50%{
transform:translateX(20px);
}

75%{
opacity:1;
}

100%{
transform:translateX(80px);
opacity:.2;
}

}

@keyframes rainbow {

0%{color:#C8102E;}
20%{color:#D2691E;}
40%{color:#228B22;}
60%{color:#1E90FF;}
80%{color:#800080;}
100%{color:#C8102E;}

}

.brain{

font-size:54px;

animation:pulse 1.6s infinite;

color:#C8102E;

}

.books{

font-size:34px;

animation:
books 2.5s linear infinite,
rainbow 4s linear infinite;

letter-spacing:8px;

}

.title{

font-size:28px;

font-weight:700;

color:#C8102E;

}

.subtitle{

font-size:18px;

color:#555;

}

.card{

padding:25px;

background:white;

border-radius:18px;

box-shadow:0 4px 18px rgba(0,0,0,.12);

border-left:8px solid #C8102E;

margin-bottom:15px;

}

</style>

<div class="card">

<center>

<div class="brain">🧠</div>

<div class="title">

RIZK AI is Building Your Knowledge Base

</div>

<br>

<div class="books">

📕📗📘📙📚

</div>

<br>

<div class="subtitle">

Please wait while your document is processed.

</div>

</center>

</div>

""",unsafe_allow_html=True)


def thinking_animation(stop_event):

    books = [
        "📕",
        "📗",
        "📘",
        "📙",
        "📚"
    ]

    messages = {tip}

    progress = st.empty()
    message = st.empty()

    p = 0

    while not stop_event.is_set():

        icon = random.choice(books)

        progress.markdown(
            f"""
<div style="font-size:38px;text-align:center;">
{icon} {"🟩"*int(p/10)}
</div>
""",
            unsafe_allow_html=True
        )

        message.markdown(
            f"""
<div style="
text-align:center;
font-size:18px;
font-weight:600;
color:#555;">
🧠 <span style="color:#C8102E;">Thinking...</span><br><br>

<span style="font-size:16px;">
{random.choice(messages)}
</span><br><br>

<span style="color:#777;">
Please wait while I search your documents.
</span>

</div>
""",
            unsafe_allow_html=True
        )

        p += random.randint(3, 10)

        if p > 98:
            p = 98

        time.sleep(0.7)

    progress.empty()
    message.empty()
stage_icons = {

"Queued":"⏳",

"Reading":"📖",

"OCR":"🔍",

"Chunk":"✂️",

"Embedding":"🧠",

"Saving":"☁️",

"Completed":"🎉"

}
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD", "supersecret123")
from app.history import UPLOAD_HISTORY_FILE

import streamlit as st

st.set_page_config(
   page_title="RIZK AI ASSISTANT",
   page_icon="favicon.ico",   # optional
   layout="wide"
)
# ======================================================
# WELCOME
# ======================================================
import random
import streamlit as st

# ==========================================================
# WELCOME
# ==========================================================

st.markdown("""
<div style="text-align:center;padding:20px 10px;">

<h1 style="
color:#C8102E;
margin-bottom:8px;
font-size:42px;">
🎓 Welcome to RIZK AI
</h1>

<h3 style="
color:#444;
margin-top:0;">
Your AI-Powered Academic Assistant
</h3>

<p style="
font-size:18px;
max-width:900px;
margin:auto;
color:#666;
line-height:1.7;">

RIZK AI searches across your instructor-approved course materials to provide
accurate, context-aware answers, explanations, programming assistance,
summaries, and personalized learning support.

Simply ask a question below to begin.

</p>

</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
    background:#fafafa;
    border-left:5px solid #C8102E;
    border-radius:12px;
    padding:22px 28px;
    margin-bottom:20px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
">

<h3 style="
    color:#C8102E;
    margin-top:0;
    margin-bottom:15px;
">
📚 RIZK AI can help you with
</h3>

<ul style="
    margin:0;
    padding-left:25px;
    line-height:2;
    font-size:18px;
    color:#333;
">

<li>📖 Textbooks &amp; Course PDFs</li>
<li>📝 Lecture Notes &amp; Slides</li>
<li>💻 Programming Assignments</li>
<li>🏠 Homework Questions</li>
<li>🧩 Practice Problems</li>
<li>🐞 Code Explanation &amp; Debugging</li>

</ul>

</div>
""", unsafe_allow_html=True)
# ==========================================================
# EXAMPLE QUESTIONS
# ==========================================================

ds1_examples = [
    "📘 Summarize supervised and unsupervised Learning.",
    "📚 What is confusion matrix?",
    "📄 Summarize supervised and unsupervised Learning.",
    "🧠 Explain K-Means algorithm.",
    "🔍 What is cluster Validity."
]

programming_examples = [
    "💻 Explain C++ queue code.",
    "🐞 Help me understand recursion using C++.",
    "⚙️ Explain binary search in C++ with examples.",
    "🌳 Compare arrays and linked lists.",
    "💾 Explain dynamic memory allocation.",
    "🔍 Compare DFS and BFS."
]

ds2_examples = [
    "📝 Explain neural network step by step.",
    "🎯 Give me a definition of convolutional neural network.",
    "📖 What is logistic regression.",
    "🏆 What is gradient descent.",
    "📑 Explain LSTM."
]

study_examples = [
    "📚 Summarize the benefits of heap sort.",
    "💡 Explain recursion like I'm a beginner.",
    "📈 Compare Merge Sort and Quick Sort.",
    "🧠 Give an example of linked lists.",
    "📋 Explain Dijkestra algorithm."
]


# Randomize every page refresh

course = random.choice(ds1_examples)
programming = random.choice(programming_examples)
exam = random.choice(ds2_examples)
study = random.choice(study_examples)

st.markdown("## 💡 Try asking one of these questions")
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

categories = [
    ("📘 Data Science I", course, "course"),
    ("💻 Data Structures Programming", programming, "programming"),
    ("📝 Data Science II", exam, "exam"),
    ("🎓 Concepts Study", study, "study"),
]

col1, col2 = st.columns(2)

for i, (title, prompt, key) in enumerate(categories):

    with (col1 if i % 2 == 0 else col2):

        st.markdown(f"### {title}")

        if st.button(
            prompt,
            key=f"btn_{key}",
            use_container_width=True
        ):
            st.session_state.selected_prompt = prompt
            st.rerun()



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
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 400px !important;
}
section[data-testid="stSidebar"] > div {
    width: 400px !important;
}
</style>
""", unsafe_allow_html=True)

# =================================
# PAGE CONFIG
# =================================
#st.set_page_config(page_title="RIZK AI", page_icon="📕", layout="wide")

# =================================
# show thinking
# =================================
import streamlit as st
import streamlit.components.v1 as components

import time
import streamlit as st


def show_thinking(tip):
    placeholder = st.empty()
    placeholder.info(f"🤔 {tip}")
    start = time.time()

    placeholder.markdown(
        f"""
<style>

@keyframes pulse {{
    0% {{transform:scale(1);}}
    50% {{transform:scale(1.18);}}
    100% {{transform:scale(1);}}
}}

@keyframes slideBooks {{

    0%   {{transform:translateX(-40px);opacity:0.3;}}

    25%  {{opacity:1;}}

    50%  {{transform:translateX(40px);}}

    75%  {{opacity:1;}}

    100% {{transform:translateX(-40px);opacity:0.3;}}
}}

@keyframes rainbow {{

0%{{color:#C8102E;}}
20%{{color:#0072CE;}}
40%{{color:#00843D;}}
60%{{color:#F6BE00;}}
80%{{color:#7C3AED;}}
100%{{color:#C8102E;}}

}}

.thinking-box{{
    text-align:center;
    padding:25px;
}}

.brain{{
    font-size:70px;
    animation:pulse 1.2s infinite;
}}

.books{{
    font-size::34px;

animation:
slideBooks 3s infinite,
rainbow 4s infinite;

margin-top:15px;

}}

.message{{
    font-size:22px;
    color:#444444;
    margin-top:18px;
    font-weight:600;
}}

.tip{{
    color:#888;
    margin-top:12px;
    font-size:16px;
}}

</style>

<div class="thinking-box">

<div class="brain" style="color:#C8102E;">
🧠
</div>

<div class="books">
📕 📗 📘 📙 📚
</div>

<div class="message">
RIZK AI is thinking...
</div>

<div class="tip">
Searching your course materials and generating the best answer.
</div>

</div>

""",
        unsafe_allow_html=True,
    )

    return placeholder, start
#st.divider()
#cols = st.columns(11)

#for i, col in enumerate(cols):
#    with col:
#        st.image("white_red_reversed.png", width= 50)

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

tips = [
    "📖 Reading your uploaded documents...",
    "🔍 Searching the most relevant chapters...",
    "🧠 Understanding the question...",
    "📚 Comparing multiple sources...",
    "✍️ Writing a concise answer...",
    "💡 Checking for the best explanation...",
]
import random
tip = random.choice(tips)
# =================================
# CHAT INPUT
# =================================

typed_query = st.chat_input(
    "Ask RIZK AI anything...",
    key="main_chat_input"
)

if st.session_state.selected_prompt:
    query = st.session_state.selected_prompt
    st.session_state.selected_prompt = None
else:
    query = typed_query

if query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    thinking, start = show_thinking(tip)

    res = requests.post(
        f"{API_URL}/query",
        json={"q": query},
        timeout=300
    )

    thinking.empty()
    elapsed = round(time.time() - start, 1)

    st.caption(
        f"⏱ Response generated in {elapsed} seconds"
    )


    if res.status_code != 200:

        st.error("Backend error")
        st.code(res.text)
        st.stop()

    data = res.json()

    answer = re.sub(
        r"dlab\d+_\d+",
        "",
        data.get("answer", "")
    ).strip()

    sources = data.get("sources", [])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "citations": sources
        }
    )

    st.rerun()
#==================
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
import hashlib
import base64

import pandas as pd
import requests

# =================================
# UPLOAD SECTION
# =================================

#st.divider()

# =================================
# ADMIN UPLOAD PANEL
# =================================
with st.sidebar:

        with open(
            "white_red_reversed2.png",
            "rb"
        ) as f:
            data = base64.b64encode(
                f.read()
            ).decode()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.image("white_red_reversed2.png", width=150)

with st.sidebar.expander(
    "📄 Upload Knowledge Files (Admin)",
    expanded=False
):
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

if st.session_state.get("authenticated", False):

    uploaded_files = st.file_uploader(
        "Drag & Drop files here",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
        key="knowledge_upload"
    )

    if uploaded_files:

        st.markdown("### 📦 Files Ready")

        for file in uploaded_files:
            ext = file.name.split(".")[-1].lower()
            icon = file_icon.get(ext, "📄")
            st.info(f"{icon} {file.name}")

        replace_existing = st.checkbox(
            "♻ Replace existing files if duplicates found"
        )

        if st.button("🚀 Upload & Ingest All"):

            overall_progress = st.progress(0)

            total_files = len(uploaded_files)

            for idx, uploaded_file in enumerate(uploaded_files):

                st.markdown(f"## 📄 {uploaded_file.name}")

                progress = st.progress(0)

                percent = st.empty()

                stage = st.empty()

                stats = st.empty()

                try:

                    files = {

                        "file": (

                            uploaded_file.name,

                            uploaded_file.getvalue(),

                            "application/octet-stream"

                        )

                    }

                    data = {

                        "replace_existing": str(
                            replace_existing
                        )

                    }

                    # ---------------------------------
                    # Start upload
                    # ---------------------------------

                    response = requests.post(

                        f"{API_URL}/upload_file",

                        files=files,

                        data=data,

                        timeout=30

                    )

                    if response.status_code != 200:
                        st.error(
                            f"❌ Failed to upload {uploaded_file.name}"
                        )

                        continue

                    job = response.json()

                    job_id = job["job_id"]


                #    with animation.container():
                #       upload_animation()
                    animation = st.empty()

                    animation.markdown(
                        "<h2>🧠 RIZK AI is Building Your Knowledge Base...</h2>",
                        unsafe_allow_html=True
                    )
                    # ---------------------------------
                    # Poll backend
                    # ---------------------------------
                    stage_map = {
                        "reading": "📖 Reading document...",
                        "ocr": "🔍 Extracting text...",
                        "chunk": "🧩 Organizing knowledge...",
                        "embedding": "🧠 Understanding content...",
                        "upload": "💾 Saving to knowledge base...",
                        "completed": "✅ Finalizing..."
                    }
                    summary_card = st.empty()
                    while True:

                        r = requests.get(f"{API_URL}/upload_progress/{job_id}")

                        if r.status_code != 200:
                            st.error("Lost connection.")
                            break

                        job = r.json()

                        p = int(job.get("progress", 0))
                        progress.progress(p)

                        current_stage = stage_map.get(
                            job.get("stage", "").lower(),
                            job.get("stage", "")
                        )

                        stage.info(current_stage)

                        percent.markdown(
                            f"""
                            <div style="text-align:center;margin-bottom:10px;">
                                <h1 style="
                                    color:#C8102E;
                                    font-size:48px;
                                    margin:0;
                                ">
                                    {p}%
                                </h1>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if job.get("status") == "completed":
                            progress.progress(100)
                            break

                        if job.get("status") == "failed":
                            st.error(job.get("stage", "Upload failed"))
                            break

                        time.sleep(1)
                    if job.get("status") == "completed":

                        pages = job.get("pages", 0)
                        chunks = job.get("chunks", 0)
                        elapsed = job.get("elapsed", 0)

                    #    st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                    #    animation.success("🎉 Knowledge Base Updated")
                        animation.empty()
                        summary_card.markdown(
                            f"""
                            <div style="
                                padding:22px;
                                background:#FAFAFA;
                                border-radius:16px;
                                border-left:7px solid #C8102E;
                                margin-top:20px;
                            ">

                            <h3 style="color:#C8102E;margin-top:0;">
                            📚 Knowledge Base Updated
                            </h3>

                            <p>
                            Your document has been completely indexed and is now available for
                            <b>RIZK AI</b>.
                            </p>

                            <div style="
                                display:flex;
                                justify-content:space-around;
                                text-align:center;
                                margin-top:20px;
                            ">

                                <div>
                                    <div style="font-size:15px;color:#888;">📄 Pages</div>
                                    <div style="font-size:36px;font-weight:bold;">
                                        {pages}
                                    </div>
                                </div>

                                <div>
                                    <div style="font-size:15px;color:#888;">🧩 Chunks</div>
                                    <div style="font-size:36px;font-weight:bold;">
                                        {chunks}
                                    </div>
                                </div>

                                <div>
                                    <div style="font-size:15px;color:#888;">⏱ Time</div>
                                    <div style="font-size:36px;font-weight:bold;">
                                        {elapsed:.1f}s
                                    </div>
                                </div>

                            </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


                    elif job.get("status") == "failed":

                        st.error(job.get("stage"))

                    overall_progress.progress(

                        int(

                            ((idx + 1) / total_files)

                            * 100

                        )

                    )

                except Exception as e:

                    st.error(

                        f"❌ {uploaded_file.name}"

                    )

                    st.code(str(e))
                overall_progress.progress(
                    int(
                        ((idx + 1) / total_files) * 100
                    )
                )

    # ==========================================
    # Upload History
    # ==========================================
    res = requests.get(f"{API_URL}/uploaded_files")

    if res.status_code == 200:
        history_df = pd.DataFrame(res.json())
    else:
        history_df = pd.DataFrame()

    st.subheader("📚 Knowledge Base Files")

    if history_df.empty:

        st.info("No uploaded files.")

    else:

        # Display the table once
        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("Delete File")

        for idx, row in history_df.iterrows():

            col1, col2 = st.columns([8, 1])

            with col1:

                st.write(
                    f"**{row['filename']}** "
                    f"({row['chunks']} chunks)"
                )

            with col2:

                if st.button(
                        "🗑",
                        key=f"delete_{idx}"
                ):

                    delete_res = requests.delete(
                        f"{API_URL}/delete_file",
                        params={
                            "file_hash": row["file_hash"]
                        }
                    )

                    if delete_res.status_code == 200:

                        st.success(
                            f"{row['filename']} deleted."
                        )

                        st.rerun()

                    else:

                        st.error("Delete failed.")

    # =========================
    # EXPORT
    # =========================

    st.subheader("📜 Export")

    st.download_button(
        label="📥 Download File List",
        data=history_df.to_csv(index=False),
        file_name="uploaded_files.csv",
        mime="text/csv"
    )

    # =========================
    # CLEAR ALL
    # =========================

    if st.button("🗑 Clear All Files"):

        clear_res = requests.delete(
            f"{API_URL}/delete_all_files"
        )

        if clear_res.status_code == 200:

            st.success("All files deleted.")

            st.rerun()

        else:

            st.error("Failed to delete files.")
# =================================
# SIDEBAR
# =================================

with st.sidebar:
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
                "🧹 Clear Chat",
                key="clear_chat_button",
                use_container_width=True
        ):
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button(
                "⬅️ Back",
                key="back_button",
                use_container_width=True
        ):
            if st.session_state.messages:
                st.session_state.messages.pop()
                st.rerun()

   # st.divider()

    # =========================
    # LOGO + TITLE
    # =========================

    try:

        with open(
            "RIZKRED2.png",
            "rb"
        ) as f:

            data = base64.b64encode(
                f.read()
            ).decode()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.image("RIZKRED2.png", width=150)
        st.markdown(
            """
            <h2 style="margin:0;">
                Dr. Nouhad Rizk
            </h2>

            <b>Piper Professor & Director of Undergraduate Studies</b><br>

            <i>Computer Science Department</i><br><br>

            🏢 <b>Office:</b> PGH 565<br>

            📍 <b>Address:</b><br>
            3551 Cullen Blvd<br>
            Houston, TX 77204<br><br>

            📞 <b>Phone:</b>
            <a href="tel:+17137433710">
                (713) 743-3710
            </a><br>

            🌐 <b>Website:</b>
            <a href="https://www.uh.edu/nouhadrizk" target="_blank">
                uh.edu/nouhadrizk
            </a>
            """,
            unsafe_allow_html=True,
        )

    except Exception:

        st.markdown(
            "📘 RIZK AI Assistant"
        )

    # =================================
    # FOOTER
    # =================================

   # st.divider()

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