# app/api/endpoints/file.py
from fastapi import APIRouter, File, Form, UploadFile, Depends
from app.services.file_service import FileService
from app.services.document_service import DocumentService
from app.services.document_processor import PDFProcessor
from app.services.embedding_service import OllamaEmbeddingService
from app.services.vector_store_service import FAISSVectorStoreService

file_router = APIRouter()

def get_document_service():
    document_processor = PDFProcessor()
    embedding_service = OllamaEmbeddingService()
    vector_store_service = FAISSVectorStoreService(embedding_service)
    return DocumentService(document_processor, vector_store_service)

def get_file_service(document_service: DocumentService = Depends(get_document_service)):
    return FileService(document_service)

@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_filename: str = Form(...),
    file_service: FileService = Depends(get_file_service)
):
    return await file_service.process_upload(file, original_filename)# app/api/endpoints/file.py
from fastapi import APIRouter, File, Form, UploadFile, Depends
from app.services.file_service import FileService
from app.services.document_service import DocumentService
from app.services.document_processor import PDFProcessor
from app.services.embedding_service import OllamaEmbeddingService
from app.services.vector_store_service import FAISSVectorStoreService

file_router = APIRouter()

def get_document_service():
    document_processor = PDFProcessor()
    embedding_service = OllamaEmbeddingService()
    vector_store_service = FAISSVectorStoreService(embedding_service)
    return DocumentService(document_processor, vector_store_service)

def get_file_service(document_service: DocumentService = Depends(get_document_service)):
    return FileService(document_service)

@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_filename: str = Form(...),
    file_service: FileService = Depends(get_file_service)
):
    return await file_service.process_upload(file, original_filename)
