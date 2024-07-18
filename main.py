import streamlit as st
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline
import PyPDF2
import os
import uvicorn
from io import BytesIO
import torch

# Initialize FastAPI
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model and tokenizer loading
checkpoint = "LaMini-Flan-T5-248M"
tokenizer = T5Tokenizer.from_pretrained(checkpoint)
base_model = T5ForConditionalGeneration.from_pretrained(checkpoint, device_map='auto', torch_dtype=torch.float32)

def file_preprocessing(file):
    pdf_reader = PyPDF2.PdfReader(BytesIO(file))
    num_pages = len(pdf_reader.pages)
    final_texts = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        final_texts += page.extract_text()
    return final_texts

def llm_pipeline(text):
    pipe_sum = pipeline(
        'summarization',
        model=base_model,
        tokenizer=tokenizer,
        max_length=500,
        min_length=50
    )
    result = pipe_sum(text)
    result = result[0]['summary_text']
    return result

@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    content = await file.read()
    input_text = file_preprocessing(content)
    summary = llm_pipeline(input_text)
    return {"summary": summary}

# Run FastAPI with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)

