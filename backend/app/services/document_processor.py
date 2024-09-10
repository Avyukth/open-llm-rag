from abc import ABC, abstractmethod
from typing import List
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor(ABC):
    @abstractmethod
    def process(self, file_path: str) -> List[Document]:
        pass

class PDFProcessor(DocumentProcessor):
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        return splitter.split_documents(pages)
