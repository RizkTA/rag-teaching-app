import plotly.express as px
import streamlit as st
import requests
import plotly.express as px
import streamlit as st
import requests

API_URL = "http://localhost:8000"
def post_json(url, payload):
    response = None
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception:
        st.error("Backend error or invalid JSON response")
        st.write("Status:", getattr(response, "status_code", None))
        st.write("Response:", getattr(response, "text", None))
        st.stop()

st.set_page_config(page_title="RAG Teaching Assistant", layout="wide")

st.title("🧠 RAG Teaching Assistant")
st.caption("Explore retrieval, generation, and hallucination in real time")

# Sidebar
st.sidebar.header("Controls")
mode = st.sidebar.selectbox(
    "Mode",
    ["Ask", "Explain", "Visualize Retrieval", "Quiz", "Evaluate Answer", "Hallucination","Embedding Visualization"]
)

# Input
query = st.text_input("Enter your question")

# ----------------------------
# ASK MODE
# ----------------------------
# ----------------------------
# CHATGPT-STYLE UI
# ----------------------------
import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🧠 RAG Teaching Assistant")
st.caption("Ask questions about your course material")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box (like ChatGPT)
if prompt := st.chat_input("Ask a question..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    res = post_json(f"{API_URL}/query", {"q": prompt})

    answer = res.get("answer", "No answer.")
    sources = res.get("sources", [])

    # Format assistant response
    formatted = f"{answer}\n\n---\n📚 **Sources:**\n"
    for s in sources:
        formatted += f"- {s}\n"

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": formatted})

    with st.chat_message("assistant"):
        st.markdown(formatted)

"""""
# ----------------------------
# ASK MODE (FINAL CLEAN VERSION)
# ----------------------------
if mode == "Ask":
    if st.button("Get Answer"):
        res = post_json(f"{API_URL}/query", {"q": query})

        st.subheader("📌 Answer")
        st.markdown(res.get("answer", "No answer returned."))

        st.markdown("---")

        st.subheader("📚 Sources")
        sources = res.get("sources", [])

        if sources:
            for s in sources:
                st.markdown(f"- {s}")
        else:
            st.write("No sources found.")
"""
# ----------------------------
# EXPLAIN MODE
# ----------------------------
elif mode == "Explain":
    if st.button("Explain RAG"):
       # res = requests.post(f"{API_URL}/explain", params={"q": query}).json()
        response = requests.post(
            f"{API_URL}/explain",
            json={"q": query}
        )

        res = response.json()
        st.subheader("📌 Final Answer")
        #st.write(res["final_answer"])
        st.markdown(res["answer"])

        st.subheader("📚 Retrieved Chunks")
        for i, chunk in enumerate(res["retrieved_chunks"]):
            st.markdown(f"**Chunk {i+1}:** {chunk}")


# ----------------------------
# VISUALIZE RETRIEVAL
# ----------------------------
elif mode == "Visualize Retrieval":
    if st.button("Show Retrieval"):
        #res = requests.post(f"{API_URL}/visualize", params={"q": query}).json()
        res = post_json(f"{API_URL}/visualize", {"q": query})
        st.subheader("🔍 Top Retrieved Chunks")
        for chunk in res["top_chunks"]:
            st.markdown(f"**Rank {chunk['rank']}**")
            st.write(chunk["text"])


# ----------------------------
# QUIZ MODE
# ----------------------------
elif mode == "Quiz":
    if st.button("Generate Quiz"):
        #res = requests.post(f"{API_URL}/quiz", params={"q": query}).json()
        res = post_json(f"{API_URL}/quiz", {"q": query})

        st.subheader("📝 Generated Quiz")
        st.write(res["quiz"])


# ----------------------------
# EVALUATE MODE
# ----------------------------
elif mode == "Evaluate Answer":
    student_answer = st.text_area("Enter student answer")

    if st.button("Evaluate"):
        #res = requests.post(
        #    f"{API_URL}/evaluate",
        #   params={"q": query, "student_answer": student_answer}
        #).json()
        res = post_json(
            f"{API_URL}/evaluate",
            {"q": query, "student_answer": student_answer}
        )

        st.subheader("📊 Evaluation")
        st.write(res["evaluation"])


# ----------------------------
# HALLUCINATION MODE
# ----------------------------
elif mode == "Hallucination":
    if st.button("Analyze"):
       # res = requests.post(f"{API_URL}/hallucination", params={"q": query}).json()
       res = post_json(f"{API_URL}/hallucination", {"q": query})
       st.subheader("📌 Answer")
       #st.write(res["answer"])
       st.markdown(res["answer"])
       st.subheader("🚨 Hallucination Analysis")
       st.write(res["analysis"])

       st.subheader("📚 Context Used")
       for c in res["contexts"]:
            st.write(f"- {c}")
elif mode == "Embedding Visualization":
    if st.button("Visualize Embeddings"):
       res = post_json(f"{API_URL}/embed_visualize", {"q": query})
       points = res["points"]
       query_pt = res["query"]

       xs = [p["x"] for p in points]
       ys = [p["y"] for p in points]
       labels = [p["text"][:80] for p in points]

       fig = px.scatter(x=xs, y=ys, text=labels)

       # Add query point
       fig.add_scatter(
            x=[query_pt["x"]],
            y=[query_pt["y"]],
            mode="markers+text",
            text=["QUERY"],
            marker=dict(size=12, symbol="x")
        )

       st.plotly_chart(fig, use_container_width=True)
       st.subheader("📌 Answer")

       if "answer" in res:
           #st.write(res["answer"])
           st.markdown(res["answer"])
       elif "error" in res:
           st.error(res["error"])
       else:
           st.error("Unexpected response from backend")

