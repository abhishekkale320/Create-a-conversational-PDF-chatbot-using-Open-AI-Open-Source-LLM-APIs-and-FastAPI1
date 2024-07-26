from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_pdf():
    with open("sample.pdf", "rb") as file:
        response = client.post("/upload_pdf/", files={"file": file})
        assert response.status_code == 200
        assert "pdf_text" in response.json()

def test_chat_with_pdf():
    pdf_text = "This is a sample PDF content."
    query = "What is this PDF about?"
    response = client.post("/chat_with_pdf/", json={"query": query, "pdf_text": pdf_text})
    assert response.status_code == 200
    assert "response" in response.json()
