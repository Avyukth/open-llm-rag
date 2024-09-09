import json
import os
from operator import itemgetter
from typing import Annotated, List, TypedDict

import requests
from fastapi import FastAPI, HTTPException
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from pydantic import BaseModel

# Configure Loguru
logger.add("app.log", rotation="500 MB")


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str
    sources: List[str]


class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (context chunk) used to answer the question",
    ]


app = FastAPI()
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://192.168.1.7:11434")
# Constants
PDF_FILE = "data/paul.pdf"
MODEL = "llama3.1:8b"

# Initialize components
try:
    logger.info("Initializing components...")
    loader = PyPDFLoader(PDF_FILE)
    pages = loader.load()
    logger.info(f"Loaded {len(pages)} pages from {PDF_FILE}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    chunks = splitter.split_documents(pages)
    logger.info(f"Split documents into {len(chunks)} chunks")

    embeddings = OllamaEmbeddings(model=MODEL, base_url=OLLAMA_BASE_URL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()
    logger.info("Created vectorstore and retriever")

    model = ChatOllama(model=MODEL, temperature=0, base_url=OLLAMA_BASE_URL)
    parser = StrOutputParser()
    logger.info("Initialized ChatOllama model and StrOutputParser")

    template = """
    You are an assistant that provides answers to questions based on
    a given context. 

    Answer the question based on the context. If you can't answer the
    question, reply "I don't know".

    Be as concise as possible and go straight to the point.

    Context: {context}

    Question: {question}
    """

    prompt = PromptTemplate.from_template(template)

    chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
        }
        | prompt
        | model.with_structured_output(AnswerWithSources)
    )
    logger.info("Created chain")
except Exception as e:
    logger.exception(f"Error during initialization: {str(e)}")
    raise


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/ollama-status")
def check_ollama_status():
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/",
            headers={"Accept": "text/html"},
            verify=False,
            timeout=5,
        )
        if response.status_code == 200:
            return {"status": "Ollama is running"}
        else:
            return {
                "status": f"Ollama is not responding correctly. Status code: {response.status_code}"
            }
    except requests.RequestException as e:
        logger.exception(f"Error checking Ollama status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error connecting to Ollama: {str(e)}"
        )


@app.post("/answer", response_model=Answer)
async def answer_question(question: Question):
    try:
        logger.info(
            f"=========================================Received question: {question.question}"
        )
        result = chain.invoke({"question": question.question})
        logger.info(f"Generated answer: {result}")

        # Ensure the result matches the expected structure
        if isinstance(result, dict) and "answer" in result and "sources" in result:
            # Parse the sources string into a list
            try:
                sources = json.loads(result["sources"])
            except json.JSONDecodeError:
                # If parsing fails, split the string by commas (adjust as needed)
                sources = [s.strip() for s in result["sources"].strip("[]").split(",")]

            return Answer(answer=result["answer"], sources=sources)
        else:
            logger.error(f"Unexpected result structure: {result}")
            raise HTTPException(
                status_code=500, detail="Unexpected response structure from the chain"
            )
    except Exception as e:
        logger.exception(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting the application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
