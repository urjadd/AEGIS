from fastapi import FastAPI, UploadFile, File
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings

app = FastAPI(title="rag-engine")
@app.get("/health")
def health():
    return {"status" : "ok"}

@app.get("/ready")
def ready():
    return {"status" : 'ready'}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    return {"status": "ingested", "filename": file.filename}

@app.post("/query")
async def query(question: str):
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    llm = ChatOpenAI(model="gpt-4o-mini")
    qdrant = QdrantVectorStore.from_existing_collection(
        collection_name="documents",
        url="http://localhost:6333",
        embedding=embeddings,
    )
    retriever = qdrant.as_retriever()
    docs = retriever.invoke(question)
    prompt = ChatPromptTemplate.from_template(
        "Context: {context}\nQuestion: {question}\nAnswer:"
    )
    chain = prompt | llm | StrOutputParser()  #LCEL (Langchain ExpressionLanguage) - chain - output becomes input of the next
    answer = chain.invoke({"context": docs, "question": question})
    return {"answer": answer, "sources": [doc.metadata for doc in docs]}
