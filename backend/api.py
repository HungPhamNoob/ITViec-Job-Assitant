import os
from typing import Iterable

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="ITViec Job AI Assistant",
    description="A retrieval-augmented assistant for AI, data, and software job discovery.",
    version="0.1.0",
)

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vector_store = FAISS.load_local(
    "db/jobs_faiss",
    embeddings,
    allow_dangerous_deserialization=True,
)
retriever = vector_store.as_retriever(search_kwargs={"k": 10})

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3,
    api_base="https://api.deepseek.com/v1",
)


class ChatRequest(BaseModel):
    message: str


def format_docs(docs: Iterable) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


prompt = PromptTemplate(
    template="""
You are an IT job recommendation assistant.

Use only the information provided in the context below.
Do not invent jobs, companies, salaries, or skills that are not present in the retrieved data.

Context:
{context}

Question:
{question}

Respond in Vietnamese.
If relevant jobs are available, include:
- Job title
- Company
- Location
- Relevant skills
- Why the role matches the request
- Application link

If no relevant job is available, say so clearly.
""",
    input_variables=["context", "question"],
)

chain = prompt | llm | StrOutputParser()


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "vectorstore": "loaded",
    }


@app.post("/chat")
def chat(req: ChatRequest) -> dict[str, str]:
    query = f"query: {req.message}"
    docs = retriever.invoke(query)
    context = format_docs(docs)

    answer = chain.invoke(
        {
            "context": context,
            "question": req.message,
        }
    )

    return {
        "question": req.message,
        "answer": answer,
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
