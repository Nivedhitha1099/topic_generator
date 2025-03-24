import os
import streamlit as st
import PyPDF2
import json
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import io

load_dotenv()
LLMFOUNDARY_TOKEN = os.getenv("LLMFOUNDARY_TOKEN")
os.environ[LLMFOUNDARY_TOKEN] = os.getenv("LLMFOUNDARY_TOKEN")

def extract_text_from_pdf(pdf_file):
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def generate_topic(question, pdf_content):
    try:
        client = OpenAI(
            api_key=f'{os.environ["LLMFOUNDARY_TOKEN"]}:my-test-project',
            base_url="https://llmfoundry.straive.com/openai/v1/",
        )

        prompt = f"Question: {question}\n\nPDF Content: {pdf_content}\n\nBased on the question and the PDF content, generate a relevant and accurate topic:"

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates relevant topics based on given information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"Error generating topic: {e}")
        return "Topic generation failed."

st.title("Topic Generator for Interview Questions")

json_file = st.file_uploader("Upload JSON file", type=["json"])
pdf_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if st.button("Generate Topics"):
    if json_file is not None and pdf_files:
        data = json.load(json_file)
        interview_questions = []
        pdf_dict = {pdf.name: pdf for pdf in pdf_files}
        for pdf in pdf_files:
            print(f"Uploaded pdf file name: {pdf.name}")

        for tab in data['tabs']:
            if tab['title'] == 'Interview':
                for content in tab['right_section_content']:
                    if 'themes' in content:
                        for theme in content['themes']:
                            if 'questions' in theme:
                                for question in theme['questions']:
                                    label = question['label']
                                    video = question['video']
                                    print(label)
                                    transcript_path = video['transcript']
                                    transcript_filename = os.path.basename(transcript_path)
                                    print(f"Transcript filename from JSON: '{transcript_filename}'")

                                    if transcript_filename and transcript_filename in pdf_dict:
                                        pdf_file = pdf_dict[transcript_filename]
                                        pdf_content = extract_text_from_pdf(pdf_file)
                                        if pdf_content:
                                            with st.spinner(f"Generating topic for: {label}"):
                                                topic = generate_topic(label, pdf_content)
                                            interview_questions.append({
                                                'Question': label,
                                                'Topic': topic
                                            })
                                    elif transcript_filename:
                                        st.warning(f"PDF file not found: {transcript_filename}")
                                    else:
                                        st.warning(f"Transcript filename not found for question: {label}")

        if interview_questions:
            df = pd.DataFrame(interview_questions)
            st.success("Topics generated successfully!")
            st.dataframe(df)

            excel_file = 'questions_topics.xlsx'
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_buffer.seek(0)

            st.download_button(
                label="Download Excel file",
                data=excel_buffer,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No interview questions found or processed.")
    else:
        st.error("Please upload a JSON file and PDF files.")

st.sidebar.header("About")
st.sidebar.info(
    "This app generates relevant topics for interview questions based on the uploaded JSON file and corresponding PDF transcripts. "
    "It uses LLM Foundry to process the inputs and create accurate topics."
)
