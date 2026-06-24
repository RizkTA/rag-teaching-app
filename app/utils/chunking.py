from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)
def chunk_texts(texts):

    if isinstance(texts, str):
        texts = [texts]

    chunks = []

    for t in texts:
        chunks.extend(
            splitter.split_text(t)
        )

    return [
        c.strip()
        for c in chunks
        if len(c.strip()) > 100
    ]