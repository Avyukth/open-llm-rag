from app.services.document_processor import DocumentProcessor, PDFProcessor


def get_document_processor(file_extension: str) -> DocumentProcessor:
    processors = {
        ".pdf": PDFProcessor,
        # Add more processors for other file types
    }
    processor_class = processors.get(file_extension.lower())
    if not processor_class:
        raise ValueError(f"Unsupported file type: {file_extension}")
    return processor_class()
