"""Small local RAG pipeline: PDF -> chunks -> embeddings -> Chroma -> Ollama answer."""
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL = "qwen3.5:2b"

PROMPT = (
    "You are a helpful assistant. Answer the question using ONLY the context below. "
    "Reply in the same language as the question. Be short and exact. "
    "If the answer is not in the context, say that you do not know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
)

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL, encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings


def load_pdf(source, name):
    """source: path or file-like object. Returns one Document per page."""
    reader = PdfReader(source)
    return [
        Document(page_content=p.extract_text() or "", metadata={"source": name, "page": i})
        for i, p in enumerate(reader.pages, start=1)
    ]


def build_store(docs, chunk_size=200, chunk_overlap=30):
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    ).split_documents(docs)
    store = Chroma.from_documents(
        chunks, get_embeddings(), collection_metadata={"hnsw:space": "cosine"}
    )
    return store, chunks


def retrieve(store, question, k=3):
    """Return [(Document, similarity 0..1)] for the k closest chunks."""
    hits = store.similarity_search_with_score(question, k=k)
    return [(doc, 1 - dist) for doc, dist in hits]  # cosine distance -> similarity


def build_prompt(question, hits):
    context = "\n---\n".join(doc.page_content for doc, _ in hits)
    return PROMPT.format(context=context, question=question)


def get_llm(model=LLM_MODEL):
    return ChatOllama(model=model, temperature=0, reasoning=False)


def stream_answer(question, hits, model=LLM_MODEL):
    for part in get_llm(model).stream(build_prompt(question, hits)):
        yield part.content


def answer(question, hits, model=LLM_MODEL):
    return "".join(stream_answer(question, hits, model))


def run_eval(store, cases, k=4, model=LLM_MODEL):
    """Yield one result dict per case; a case passes if any expected fact is in the answer."""
    for case in cases:
        hits = retrieve(store, case["q"], k=k)
        text = answer(case["q"], hits, model)
        yield {
            "question": case["q"],
            "answer": text.strip(),
            "expected": " / ".join(case["must"]),
            "passed": any(m.lower() in text.lower() for m in case["must"]),
        }
