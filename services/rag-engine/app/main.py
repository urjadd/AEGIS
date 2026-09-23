from fastapi import FastAPI, UploadFile, File
from langchain_qdrant import QdrantVectoreStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI