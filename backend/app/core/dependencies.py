from fastapi import HTTPException
from app.services.qa_service import QAService

qa_service_instance = None

def get_qa_service():
    global qa_service_instance
    if qa_service_instance is None:
        raise HTTPException(status_code=400, detail="No document has been processed yet. Please upload a file first.")
    return qa_service_instance

def set_qa_service(new_qa_service: QAService):
    global qa_service_instance
    qa_service_instance = new_qa_service
