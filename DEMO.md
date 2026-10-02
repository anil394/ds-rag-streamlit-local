# 5-minute demo script

Before you start: open the Ollama app, run `uv run streamlit run app.py`, wait until the page shows the document cards (first load takes about 20 seconds), and ask one warm-up question so the model is loaded.

| Time | On screen | What to say |
|---|---|---|
| 0:00 | Banner and cards | "Companies have private documents they can not paste into ChatGPT. I built an assistant that answers questions about a PDF and runs fully on this laptop, with a small open-source model. Nothing leaves the machine." |
| 0:40 | Cards: 6 chunks, top 4 | "RAG means the AI does not guess. First the PDF is cut into small chunks, here 6. Each chunk is turned into numbers and stored in a vector database. For each question I find the 4 closest chunks and give only those to the model." |
| 1:20 | Ask: "How many days of paid leave do I get per year?" | "Answer: 28 days. The model read only the closest chunks, not the whole file." |
| 1:50 | Open "Sources" | "Here is what it was allowed to read, with a similarity score. That makes the answer checkable, so it can not just make things up." |
| 2:20 | Ask in German: "Wie hoch ist das Hotelbudget pro Nacht?" | "The PDF is English, my question is German, and the answer comes back in German. The embedding model understands meaning across languages." |
| 3:00 | Tab "How the PDF was chunked" | "This is what the system actually sees: small chunks, each one idea. Chunking is a key design choice." |
| 3:30 | Tab "Live accuracy check", click "Run accuracy check" | "Instead of saying it works, I measure it: 8 English and German questions, each with a known correct fact. Watch the counter: 8 out of 8." |
| 4:15 | Turn Wi-Fi off, ask one more question | "Wi-Fi is off and it still works, so the model, the search and the data are all local." |
| 4:40 | Back to banner | "Limits: a 2 billion parameter model is small and the check is simple keyword matching. Next steps: a bigger model, more documents, and a proper evaluation." |

## Backup answers if someone asks

- Why local? Privacy, no cost per question, works offline.
- Why not just ChatGPT? Confidential files, and RAG shows its sources.
- What is a vector? A list of numbers that captures the meaning of a text, so similar meanings sit close together.
- What if the answer is wrong? Check the Sources tab: either the right chunk was not found (retrieval problem) or the model misread it (generation problem).
