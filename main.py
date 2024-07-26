from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import PyPDF2
import requests
from io import BytesIO
import openai

app = FastAPI()

# Use your updated OpenAI API key and endpoint here
OPENAI_API_KEY = ""
OPENAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def query_openai_api(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # or "gpt-4"
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

def generate_response_with_rag(pdf_text, user_query):
    prompt = f"Context: {pdf_text}\n\nQuery: {user_query}\n\nAnswer:"
    response = query_openai_api(prompt)
    return response

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pdf_file = BytesIO(contents)
        text = extract_text_from_pdf(pdf_file)
        return JSONResponse(content={"message": "PDF processed successfully", "pdf_text": text})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class QueryRequest(BaseModel):
    query: str
    pdf_text: str

@app.post("/chat_with_pdf/")
async def chat_with_pdf(request: QueryRequest):
    try:
        response = query_openai_api(f"Context: {request.pdf_text}\n\nQuery: {request.query}")
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
