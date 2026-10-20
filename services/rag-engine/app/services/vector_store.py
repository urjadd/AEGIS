from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

def store_chunks(texts: list[str], metadatas = list[dict]) -> int:
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    QdrantVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas = metadatas,
        url="http://localhost:6333",
        collection_name="documents"
    )
    return len(texts)
    