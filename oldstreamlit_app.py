import streamlit as st
import requests

# ----------------------------
# CONFIG
# ----------------------------
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="RIZK Teaching Assistant",
    page_icon="📕",
    layout="wide"
)

# ----------------------------
# HELPER FUNCTION
# ----------------------------
def post_json(url, payload):
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("⚠️ Backend error")
        try:
            st.write(response.text)
        except:
            pass
        return {}

# ----------------------------
# SESSION STATE (CHAT MEMORY)
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# UI HEADER
# ----------------------------
st.title("📕 RIZK Teaching Assistant")
st.caption("Your AI-powered course assistant (ChatGPT-style)")

# ----------------------------
# DISPLAY CHAT HISTORY
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----uv run uvicorn main:app –reload-----------------------
# CHAT INPUT
# ----------------------------
if prompt := st.chat_input("Ask a question about your material..."):

    # ----------------------------
    # USER MESSAGE
    # ----------------------------
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # ----------------------------
    # BACKEND CALL
    # ----------------------------
    res = post_json(f"{API_URL}/query", {"q": prompt})

    # ----------------------------
    # FORMAT RESPONSE (FIXED)
    # ----------------------------
    if "error" in res:
        formatted_answer = f"⚠️ {res['error']}"
    else:
        answer = res.get("answer")
        sources = res.get("sources", [])

        if not answer:
            formatted_answer = "⚠️ No answer returned from backend."
        else:
            formatted_answer = str(answer).strip()

        # Add sources cleanly
        if sources:
            formatted_answer += "\n\n---\n📚 **Sources:**\n"
            for s in sources:
                formatted_answer += f"- {s}\n"
    # ----------------------------
    # ASSISTANT MESSAGE
    # ----------------------------
    st.session_state.messages.append({
        "role": "assistant",
        "content": formatted_answer
    })

    with st.chat_message("assistant"):
        st.markdown(formatted_answer)

# ----------------------------
# SIDEBAR (OPTIONAL CONTROLS)
# ----------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        "This assistant uses Retrieval-Augmented Generation (RAG) "
        "to answer questions based on your course documents."
    )