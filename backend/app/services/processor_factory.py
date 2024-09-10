from app.services.processors.pdf_processor import PDFProcessor


def get_file_processor(file_extension):
    if file_extension.lower() == '.pdf':
        return PDFProcessor()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
