import os

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

DATA_PATH = "data/itviec_jobs.csv"
INDEX_DIR = "db/jobs_faiss"


def build_documents() -> list[Document]:
    dataframe = pd.read_csv(DATA_PATH).fillna("")
    documents: list[Document] = []

    for _, row in dataframe.iterrows():
        content = f"""
passage:
Title: {row['title']}
Company: {row['company']}
Location: {row['location']}
Skills: {row['skills']}
Description: {row['description']}
Requirements: {row['requirements']}
Benefits: {row['benefits']}
Link: {row['link']}
""".strip()

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "title": row["title"],
                    "company": row["company"],
                    "location": row["location"],
                    "skills": row["skills"],
                    "link": row["link"],
                },
            )
        )

    return documents


def main() -> None:
    documents = build_documents()

    print(f"Loaded {len(documents)} records from {DATA_PATH}.")
    print("Loading the embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print("Building the FAISS vector index...")
    vector_store = FAISS.from_documents(documents, embeddings)

    os.makedirs("db", exist_ok=True)
    vector_store.save_local(INDEX_DIR)

    print(f"Saved the vector index to {INDEX_DIR}.")


if __name__ == "__main__":
    main()
