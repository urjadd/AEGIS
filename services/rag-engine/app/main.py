from fastapi import FastAPI, UploadFile, File
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="rag-engine")
embeddings = OpenAIEmbeddings()

llm = ChatOpenAI(model="gpt-4o-mini")

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    return {"status": "ingested", "filename": file.filename}

@app.post("/query")
async def query(question: str):
    qdrant = QdrantVectorStore.from_existing_collection(
        collection_name="documents",
        url="http://localhost:6333",
        embedding=embeddings
    )
    retriever = qdrant.as_retriever()
    docs = retriever.invoke(question)
    prompt = ChatPromptTemplate.from_template(
        "Context: {context}\nQuestion: {question}\nAnswer:"
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": docs, "question": question})
    return {"answer": answer, "sources": [doc.metadata for doc in docs]}
