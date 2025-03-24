import streamlit as st
import os
import PyPDF2
from openai import OpenAI

from dotenv import load_dotenv


load_dotenv()
LLMFOUNDARY_TOKEN = os.getenv("LLMFOUNDARY_TOKEN")
os.environ[LLMFOUNDARY_TOKEN] = os.getenv("LLMFOUNDARY_TOKEN")

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_title(question, pdf_content):
    client = OpenAI(
        api_key=f'{os.environ["LLMFOUNDARY_TOKEN"]}:my-test-project',
        base_url="https://llmfoundry.straive.com/openai/v1/",
    )

    prompt = f"Question: {question}\n\nPDF Content: {pdf_content}\n\nBased on the question and the PDF content, generate a relevant and accurate title:"

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates relevant titles based on given information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50  
    )

    return chat_completion.choices[0].message.content.strip()

st.title("Title Generator")


question = st.text_input("Enter your question:", "")


pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

if st.button("Generate Title"):
    if question and pdf_file is not None:
       
        pdf_content = extract_text_from_pdf(pdf_file)
        
        
        with st.spinner("Generating title..."):
            title = generate_title(question, pdf_content)
        
        
        st.success("Title generated successfully!")
        st.subheader("Generated Title:")
        st.write(title)
    else:
        st.error("Please provide both a question and a PDF file.")

st.sidebar.header("About")
st.sidebar.info(
    "This app generates a relevant title based on your question and the content of the uploaded PDF file. "
    "It uses LLM Foundry to process the inputs and create an accurate title."
)