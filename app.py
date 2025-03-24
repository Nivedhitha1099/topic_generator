import os
import streamlit as st
import json
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import io
import docx

load_dotenv()
LLMFOUNDARY_TOKEN = os.getenv("LLMFOUNDARY_TOKEN")
os.environ[LLMFOUNDARY_TOKEN] = os.getenv("LLMFOUNDARY_TOKEN")

def extract_text_from_docx(docx_file):
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def generate_topic(question, docx_content):
    try:
        client = OpenAI(
            api_key=f'{os.environ["LLMFOUNDARY_TOKEN"]}:my-test-project',
            base_url="https://llmfoundry.straive.com/openai/v1/",
        )

        prompt = f"""Question: {question}\n\nDocument Content: {docx_content}\n\nBased on the question and the document content, generate a relevant and accurate topic:
        Topic:      (maintain same format)"""

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
docx_files = st.file_uploader("Upload DOCX files", type=["docx"], accept_multiple_files=True)

if st.button("Generate Topics"):
    if json_file is not None and docx_files:
        data = json.load(json_file)
        interview_questions = []
        docx_dict = {os.path.splitext(docx_file.name)[0]: docx_file for docx_file in docx_files}
        for docx_file in docx_files:
            print(f"Uploaded docx file name: {docx_file.name}")

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
                                    transcript_filename = os.path.splitext(transcript_filename)[0]
                                    print(f"Transcript filename from JSON: '{transcript_filename}'")

                                    if transcript_filename and transcript_filename in docx_dict:
                                        docx_file = docx_dict[transcript_filename]
                                        docx_content = extract_text_from_docx(docx_file)
                                        if docx_content:
                                            with st.spinner(f"Generating topic for: {label}"):
                                                topic = generate_topic(label, docx_content)
                                            interview_questions.append({
                                                'Question': label,
                                                'Topic': topic
                                            })
                                    elif transcript_filename:
                                        st.warning(f"DOCX file not found: {transcript_filename}")
                                    else:
                                        st.warning(f"Transcript filename not found for question: {label}")

        if interview_questions:
            df = pd.DataFrame(interview_questions)
            st.success("Topics generated successfully!")
            st.dataframe(df)

            excel_file = 'questions_topics1.xlsx'
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
        st.error("Please upload a JSON file and DOCX files.")

st.sidebar.header("About")
st.sidebar.info(
    "This app generates relevant topics for interview questions based on the uploaded JSON file and corresponding DOCX transcripts. "
    "It uses LLM Foundry to process the inputs and create accurate topics."
)
