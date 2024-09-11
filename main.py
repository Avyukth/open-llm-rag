from operator import itemgetter
from typing import List

from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain_core.runnables import RunnablePassthrough
from typing_extensions import Annotated, TypedDict

PDF_FILE = "data/paul.pdf"

# We'll be using Llama 3.1 8B for this example.
MODEL = "llama3.1:8b"


loader = PyPDFLoader(PDF_FILE)
pages = loader.load()

print(f"Number of pages: {len(pages)}")
print(f"Length of a page: {len(pages[1].page_content)}")
print("Content of a page:", pages[1].page_content)


splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)

chunks = splitter.split_documents(pages)
print(f"Number of chunks: {len(chunks)}")
print(f"Length of a chunk: {len(chunks[1].page_content)}")
print("Content of a chunk:", chunks[1].page_content)


embeddings = OllamaEmbeddings(model=MODEL, base_url="http://192.168.1.7:11434")
vectorstore = FAISS.from_documents(chunks, embeddings)


retriever = vectorstore.as_retriever()
retriever.invoke(
    "What can you get away with when you only have a small number of users?"
)


model = ChatOllama(model=MODEL, temperature=0)
model.invoke("Who is the president of the United States?")


parser = StrOutputParser()

chain = model | parser
print(chain.invoke("Who is the president of the United States?"))


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
print(prompt.format(context="Here is some context", question="Here is a question"))


chain = prompt | model | parser

chain.invoke(
    {"context": "Anna's sister is Susan", "question": "Who is Susan's sister?"}
)


class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (context chunk) used to answer the question",
    ]


chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
    | prompt
    | model.with_structured_output(AnswerWithSources)
)


questions = [
    "What can you get away with when you only have a small number of users?",
    "What's the most common unscalable thing founders have to do at the start?",
    "What's one of the biggest things inexperienced founders and investors get wrong about startups?",
]

for question in questions:
    print(f"Question: {question}")
    print(f"Answer: {chain.invoke({'question': question})}")
    print("*************************\n")


# Desired schema for response
class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (author + year) used to answer the question",
    ]


# rag_chain_from_docs = (
#     {
#         "input": lambda x: x["input"],
#         "context": lambda x: format_docs(x["context"]),
#     }
#     | prompt
#     | llm.with_structured_output(AnswerWithSources)
# )

# retrieve_docs = (lambda x: x["input"]) | fa

# chain = RunnablePassthrough.assign(context=retrieve_docs).assign(
#     answer=rag_chain_from_docs
# )

# response = chain.invoke({"input": "What is Chain of Thought?"})


chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
    }
    | prompt
    | model.with_structured_output(AnswerWithSources)
)

questions = [
    "What can you get away with when you only have a small number of users?",
    "What's the most common unscalable thing founders have to do at the start?",
    "What's one of the biggest things inexperienced founders and investors get wrong about startups?",
]

for question in questions:
    print(f"Question: {question}")
    print(f"Answer: {chain.invoke({'question': question})}")
    print("*************************\n")
