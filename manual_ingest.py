from app.ingestion.ingest import ingest_pdf

#pdf_path = "/data/Reading - Data Science.pdf"
pdf_path = r"C:\Users\RIZK\PycharmProjects\rag-teaching-app\data\Reading - Data Science.pdf"
print("STARTING INGESTION...")

result = ingest_pdf(pdf_path)

print("DONE:", result)