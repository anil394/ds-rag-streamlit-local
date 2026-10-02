import json
import time
from pathlib import Path

import streamlit as st

import rag

st.set_page_config(page_title="Local RAG Demo", page_icon=":books:", layout="wide")
st.markdown(
    """
    <style>
    .hero {background: linear-gradient(120deg,#4F46E5,#7C3AED 55%,#06B6D4); color:white;
           padding:22px 28px; border-radius:16px; margin-bottom:14px;}
    .hero h1 {color:white; margin:0; font-size:2rem;}
    .hero p {margin:6px 0 0 0; opacity:.92;}
    .pill {display:inline-block; background:rgba(255,255,255,.2); border-radius:999px;
           padding:3px 12px; margin:10px 6px 0 0; font-size:.8rem;}
    .card {background:white; border-radius:14px; padding:14px 18px; border-left:6px solid #4F46E5;
           box-shadow:0 1px 6px rgba(31,35,64,.08);}
    .card.c2 {border-left-color:#7C3AED;} .card.c3 {border-left-color:#06B6D4;}
    .card small {color:#6B7280; text-transform:uppercase; letter-spacing:.05em; font-size:.7rem;}
    .card div {font-size:1.35rem; font-weight:700; color:#1F2340; overflow-wrap:anywhere;}
    [data-testid="stSidebar"] {background:#E8EBFA;}
    </style>
    <div class="hero">
      <h1>Ask your PDF, fully offline</h1>
      <p>Private document Q&A in English and German. Nothing leaves this laptop.</p>
      <span class="pill">Local LLM: qwen3.5:2b</span><span class="pill">Ollama</span>
      <span class="pill">Chroma vector DB</span><span class="pill">Multilingual embeddings</span>
    </div>
    """,
    unsafe_allow_html=True,
)

SAMPLES = {
    "Handbook (English)": "documents/nordlicht_handbook_en.pdf",
    "Handbuch (Deutsch)": "documents/nordlicht_handbuch_de.pdf",
}

with st.sidebar:
    st.header("1. Choose a document")
    upload = st.file_uploader("Upload your own PDF", type="pdf")
    sample = st.selectbox("...or use a sample", list(SAMPLES))
    st.header("2. Settings")
    k = st.slider("Chunks to retrieve (k)", 1, 6, 4)
    chunk_size = st.slider("Chunk size (characters)", 100, 600, 200, step=50)


@st.cache_resource(show_spinner="Reading, chunking and embedding the PDF...")
def prepare(source_key, data, chunk_size):
    if data is None:
        docs = rag.load_pdf(source_key, Path(source_key).name)
    else:
        import io
        docs = rag.load_pdf(io.BytesIO(data), source_key)
    return rag.build_store(docs, chunk_size=chunk_size)


if upload:
    store, chunks = prepare(upload.name, upload.getvalue(), chunk_size)
    doc_name = upload.name
else:
    store, chunks = prepare(SAMPLES[sample], None, chunk_size)
    doc_name = Path(SAMPLES[sample]).name

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="card"><small>Document</small><div>{doc_name}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card c2"><small>Chunks created</small><div>{len(chunks)}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card c3"><small>Chunks retrieved per question</small><div>top {k}</div></div>', unsafe_allow_html=True)
st.write("")

chat_tab, eval_tab, chunk_tab = st.tabs(["Ask a question", "Live accuracy check", "How the PDF was chunked"])

with chat_tab:
    st.write("Try: *How many days of paid leave do I get?* or *Wie hoch ist das Hotelbudget pro Nacht?*")
    question = st.chat_input("Ask a question in English or German")
    if question:
        st.chat_message("user").write(question)
        hits = rag.retrieve(store, question, k=k)
        with st.chat_message("assistant"):
            start = time.time()
            st.write_stream(rag.stream_answer(question, hits))
            st.caption(f"Answered locally in {time.time() - start:.1f}s")
        with st.expander("Sources: the chunks the model was allowed to read"):
            for doc, score in hits:
                st.markdown(f"**Page {doc.metadata['page']}** | similarity `{score:.2f}`")
                st.progress(max(0.0, min(1.0, score)))
                st.code(doc.page_content, language=None)

with eval_tab:
    st.write("Runs preset English and German questions and checks whether the answer contains the correct fact from the document. Works with the sample handbooks.")
    cases = json.loads(Path("eval_set.json").read_text())
    if st.button("Run accuracy check"):
        passed, rows = 0, []
        bar = st.progress(0.0)
        status = st.empty()
        table = st.empty()
        for i, r in enumerate(rag.run_eval(store, cases, k=k), start=1):
            passed += r["passed"]
            rows.append({"OK": "yes" if r["passed"] else "no", "Question": r["question"],
                         "Expected fact": r["expected"], "Model answer": r["answer"]})
            bar.progress(i / len(cases))
            status.metric("Correct so far", f"{passed} / {i}")
            table.dataframe(rows, use_container_width=True, hide_index=True)
        st.success(f"Final accuracy: {passed}/{len(cases)} = {100 * passed / len(cases):.0f}%")

with chunk_tab:
    st.write("Each box is one chunk. This is exactly what gets turned into numbers and stored.")
    for i, c in enumerate(chunks, start=1):
        st.markdown(f"**Chunk {i}** (page {c.metadata['page']}, {len(c.page_content)} characters)")
        st.code(c.page_content, language=None)
