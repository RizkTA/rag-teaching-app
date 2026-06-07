import streamlit as st
import requests

from app.rag.rag_service import answer

#API_URL = "http://localhost:8000"

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="RIZK Teaching Assistant",
    page_icon="📕",
    layout="wide"
)

st.title("📕 RIZK Teaching Assistant ")


# upload with password
#uploaded_file = st.file_uploader("📄 Upload PDF ...", type=["pdf"])

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.subheader("🔐 Upload Security")
# -----------------------------
# PASSWORD INPUT
# -----------------------------
password = st.text_input("Enter upload password", type="password")

# -----------------------------
# UPLOAD ONLY IF PASSWORD OK
# -----------------------------
if password:

    uploaded_file = st.file_uploader("📄 Upload PDF (Auto Ingest)", type=["pdf"])

    if uploaded_file is not None:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        headers = {
            "X-API-Key": str(password).strip()
        }

       # st.write("DEBUG PASSWORD:", password)
       # st.write("HEADERS:", headers)

        with st.spinner("Indexing PDF... ⚡"):
            res = requests.post(
                f"{API_URL}/upload_pdf",
                files=files,
                headers=headers
            )

        if res.status_code == 200:
            st.success("✅ PDF uploaded & indexed")
        else:
            st.error(f"❌ Upload failed: {res.text}")
# -----------------------------
# SESSION STATE (CHAT MEMORY)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# SIDEBAR (LIGHTWEIGHT)
# -----------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

    st.markdown("---")
  #  st.markdown("🧠 Local RAG System (Ollama + Qdrant)")
    import base64
    import streamlit as st

    with open("RIZKRED.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;">
            <img src="data:image/png;base64,{data}" width="100">
            <span style="margin-left:8px;"> Dr. Nouhad Rizk    Learning Companion ! </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# CHAT DISPLAY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -----------------------------
# QUERY INPUT
# -----------------------------
query = st.chat_input("Ask your documents...")

if query:

    # show user message
    st.chat_message("user").markdown(query)

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
## -----------------------------
# FAST RAG CALL (NO CACHE = ALWAYS FRESH)
# -----------------------------
with st.chat_message("assistant"):
 with st.spinner("Thinking... Generating response...🧠"):
    #   col1, col2 = st.columns([1, 20])

   #    with col1:
     #      st.image("Rizk.png", width=30)

    #   with col2:
    #       st.write("Thinking...")

     #  with st.spinner("Generating response..."):
           try:
                result = answer(query)
                response_text = result.get("answer", "")
                citations = result.get("citations", [])
           except Exception as e:
                response_text = f"❌ Error: {str(e)}"
                citations = []
           st.markdown(response_text)

           # -----------------------------
           # SOURCES (LIGHTWEIGHT)
           # -----------------------------
           if citations:
                with st.expander("📚 Sources"):
                    for c in citations[:5]:  # limit for speed
                        st.markdown(
                            f"""
**📄 {c.get('source','unknown')}**  
Chunk: {c.get('chunk_id','-')}  
Score: {round(c.get('score',0),3)}

> {c.get('preview','')[:200]}...
"""
                       )
                st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })