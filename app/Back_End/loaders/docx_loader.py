from docx import Document


def load_docx(file_path: str) -> str:
    """
    Read a DOCX file and return its text.
    """

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text