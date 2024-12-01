def get_pdf_content(pdf_id, pdf_storage):
    if pdf_id not in pdf_storage:
        raise Exception("PDF not found.")
    return pdf_storage[pdf_id]["content"]
