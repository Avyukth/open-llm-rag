from typing import Annotated, List, TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from operator import itemgetter

from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str


class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (context chunk) used to answer the question",
    ]


app = FastAPI()

# Constants
PDF_FILE = "data/paul.pdf"
MODEL = "llama3.1:8b"

# Initialize components
loader = PyPDFLoader(PDF_FILE)
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
chunks = splitter.split_documents(pages)

embeddings = OllamaEmbeddings(model=MODEL, base_url="http://192.168.1.7:11434")
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

model = ChatOllama(model=MODEL, temperature=0)
parser = StrOutputParser()

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/answer", response_model=Answer)
async def answer_question(question: Question):
    try:
        result = chain.invoke({"question": question.question})
        return Answer(answer=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
