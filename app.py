import json
import os
import uuid
from operator import itemgetter
from typing import Annotated, List, TypedDict

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
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
UPLOAD_DIR = "uploads"
WEBHOOK_URL = "http://localhost:8501/webhook"  # Update this to your Streamlit app's webhook endpoint
MODEL = "llama3.1:8b"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global variables to store the initialized components
vectorstore = None
chain = None


def initialize_components(file_path):
    global vectorstore, chain

    try:
        logger.info("Initializing components...")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        logger.info(f"Loaded {len(pages)} pages from {file_path}")

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


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), original_filename: str = Form(...)):
    try:
        # Use the provided original filename
        file_name, file_extension = os.path.splitext(original_filename)

        # If no extension is detected, use the content type to guess
        if not file_extension:
            content_type = file.content_type
            logger.warning(
                f"No file extension detected for {original_filename}. Content-Type: {content_type}"
            )
            if content_type == "application/pdf":
                file_extension = ".pdf"
            elif content_type.startswith("image/"):
                file_extension = f".{content_type.split('/')[-1]}"
            else:
                file_extension = ".bin"  # Generic binary file extension

        logger.info(f"Original filename: {original_filename}")
        logger.info(f"Detected file extension: {file_extension}")

        # Generate a unique filename with the original extension
        unique_filename = f"{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)

        logger.info(f"File saved as: {file_path}")

        # Initialize components with the new file
        initialize_components(file_path)

        # Send webhook notification
        response = requests.post(
            WEBHOOK_URL,
            json={"status": "success", "message": "File processed successfully"},
        )
        logger.info(f"Webhook response: {response.status_code} - {response.text}")

        return {
            "original_filename": original_filename,
            "saved_filename": unique_filename,
            "detected_extension": file_extension,
            "status": "File uploaded and processed successfully",
        }
    except Exception as e:
        logger.exception(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
    if not vectorstore or not chain:
        raise HTTPException(
            status_code=400,
            detail="No document has been processed yet. Please upload a file first.",
        )

    try:
        logger.info(f"Received question: {question.question}")
        result = chain.invoke({"question": question.question})
        logger.info(f"Generated answer: {result}")

        if isinstance(result, dict) and "answer" in result and "sources" in result:
            try:
                sources = json.loads(result["sources"])
            except json.JSONDecodeError:
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
