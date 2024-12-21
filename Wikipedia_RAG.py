import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

# Step 1: Scrape the Wikipedia Article
def scrape_wikipedia_article(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find("div", class_="mw-parser-output").find_all("p")
        article_content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        with open("Wikipedia_Article.txt", "w", encoding="utf-8") as file:
            file.write(article_content)
        print("Scraped article saved to 'Wikipedia_Article.txt'.")
        return article_content
    else:
        print(f"Failed to fetch the article. HTTP Status Code: {response.status_code}")
        return ""

# Step 2: Generate Embeddings and Store Locally
def generate_embeddings(article_text):
    # Split the content into chunks
    chunks = article_text.split("\n\n")
    # Load SentenceTransformers model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    # Generate embeddings for each chunk
    embeddings = model.encode(chunks)
    # Store chunks and embeddings
    document_store = [{"text": chunk, "embedding": emb} for chunk, emb in zip(chunks, embeddings)]
    print("Embeddings generated and stored in memory.")
    return document_store, model

# Step 3: Query the System and Generate Responses
def query_system(query, document_store, model, generator):
    # Generate query embedding
    query_embedding = model.encode([query])[0]
    # Calculate cosine similarities
    similarities = [cosine_similarity([query_embedding], [doc["embedding"]])[0][0] for doc in document_store]
    # Find the top match
    top_match_index = similarities.index(max(similarities))
    top_chunk = document_store[top_match_index]["text"]
    # Generate a response
    prompt = f"Context: {top_chunk}\n\nQuestion: {query}\nAnswer:"
    response = generator(prompt, max_length=50, num_return_sequences=1)
    return top_chunk, response[0]["generated_text"]

# Main Function
if __name__ == "__main__":
    # Scrape the article
    url = "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"
    article_text = scrape_wikipedia_article(url)

    if article_text:
        # Generate embeddings
        document_store, model = generate_embeddings(article_text)

        # Load the HuggingFace model
        generator = pipeline("text2text-generation", model="google/flan-t5-small")

        # Example Queries
        example_queries = ["What is RAG?", "What is indexing?"]

        # Run the queries and display results
        for query in example_queries:
            retrieved, response = query_system(query, document_store, model, generator)
            print(f"Query: {query}")
            print(f"Retrieved Content: {retrieved}")
            print(f"Generated Response: {response}\n")
