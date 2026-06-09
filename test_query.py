from app.rag.query_engine import retrieve_context

question = "What software is used in the course?"

context = retrieve_context(question)

print(context)