import logging
import warnings
from transformers import logging as hf_logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from transformers import pipeline

# 3.1 Suppress noisy logs
logging.getLogger("langchain.text_splitter").setLevel(logging.ERROR)
hf_logging.set_verbosity_error()
warnings.filterwarnings("ignore")

# 3.2 Parameters
chunk_size = 500
chunk_overlap = 50
model_name = "sentence-transformers/all-distilroberta-v1"
top_k = 5

# 3.3 Read the pre-scraped document
with open("Selected_Document.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 3.4 Split into appropriately-sized chunks
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)
chunks = splitter.split_text(text)

# 3.5 Embed & build FAISS index
print("Encoding text chunks...")
model = SentenceTransformer(model_name)
embeddings = model.encode(chunks, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# 3.6 Load the generator pipeline
generator = pipeline("text2text-generation", model="google/flan-t5-small", device=-1)

# 3.7 Retrieval & answering functions
def retrieve_chunks(question, k=top_k):
    question_embedding = model.encode([question]).astype("float32")
    distances, indices = index.search(question_embedding, k)
    return [chunks[i] for i in indices[0]]

def answer_question(question):
    context_chunks = retrieve_chunks(question)
    context = "\n\n".join(context_chunks)
    prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {question}"
    response = generator(prompt, max_length=200, do_sample=False)
    return response[0]['generated_text']

# 3.8 Interactive loop
if __name__ == "__main__":
    print("Ask me anything about the document. Type 'exit' or 'quit' to end.")
    while True:
        question = input("Your question: ")
        if question.lower() in ("exit", "quit"):
            break
        print("Answer:", answer_question(question))

