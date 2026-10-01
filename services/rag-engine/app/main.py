from fastapi import FastAPI, UploadFile, File
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

app = FastAPI(title="rag-engine")
@app.get("/health")
def health():
    return {"status" : "ok"}

@app.get("/ready")
def ready():
    return {"status" : 'ready'}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    doc = pymupdf.open(stream = await file.read(), filetype = "pdf")
    all_text ="\n".join( page.get_text() for page in doc)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 512,
        chunk_overlap = 50,
        length_function = len
    )

    texts = text_splitter.split_text(all_text)
    return {"status": "ingested", 
            "filename": file.filename, 
            "chunk_count": len(texts),
            'chuncks': texts}

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
