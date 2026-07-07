import sqlite3 as sq
connections=sq.connect("resume.db")
cursor=connections.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS resume_data(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               candidate_name TEXT,
               job_role TEXT,
               match_percentage INTEGER,
               missing_skills TEXT,
               suggestion TEXT
               )
               """)
connections.commit()

connections.close()

#module2
import io
import streamlit as st 
import fitz
from PIL import Image
st.title("===== AI Resume Analyzer =====")
upload_file=st.file_uploader("UPLOAD YOUR RESUME(PDF)",type=["pdf"])

job=st.text_area("Enter job Description:\n")

text = ""
images = []

if upload_file is not None:
    pdf_bytes = upload_file.getvalue()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # First try normal text extraction
    for page in doc:
        text += page.get_text()

    # Only create images if PDF has almost no readable text
    if len(text.strip()) < 100:
        for page in doc:
            # Lower resolution than Matrix(2, 2), so it's faster
            pix = page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3))

            img = Image.open(
                io.BytesIO(pix.tobytes("jpeg"))
            )

            images.append(img)

    doc.close()

    st.success("Resume uploaded successfully")


#module6
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("api_key")) 
model=genai.GenerativeModel("gemini-2.5-flash")

if upload_file is not None:
    if st.button("Analyze resume"):

        if not job.strip():
            st.warning("Please enter a job description.")
            st.stop()

        with st.spinner("Analyzing resume..."):
            try:
                if text.strip():
                    # Text-based PDF
                    prompt = f"""
Analyze this resume against the job description.

Resume:
{text[:12000]}

Job Description:
{job}

Return the complete analysis in exactly this format

1. Match Percentage:<number>%

2. Missing Skills :
   skills1
   skills2
   skills3

3. Matching Skills :
   skills1
   skill2
   skill3

4. Strengths :
   points
   points
   points

5. Weaknesses :
   point
   point
   point

6. Suggestions :
   point
   point
   point 

Keep the response short and professional.
important: complete all the 6 sections, donot write any introduction and conclusion


"""

                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "max_output_tokens": 400,
                            "temperature": 0.2
                        }
                    )

                else:
                    # Scanned/image-based PDF
                    prompt = f"""
Read this resume image and analyze it against the job description.

Job Description:
{job}

Return the complete analysis in exactly this format

1. Match Percentage:<number>%

2. Missing Skills : 
   skills1
   skills2
   skills3

3. Matching Skills :
   skills1
   skill2
   skill3

4. Strengths :
   points
   points
   points

5. Weaknesses :
   point
   point
   point

6. Suggestions :
   point
   point
   point 

Keep the response short and professional.
important: complete all the 6 sections, donot write any introduction and conclusion
"""

                    response = model.generate_content(
                        [prompt] + images[:2],
                        generation_config={
                            "max_output_tokens": 2000,
                            "temperature": 0.2
                        }
                    )

                #save database
                
                st.write(response.text)

                # Save result to database
                conn = sq.connect("resume.db")
                cursor = conn.cursor()

                cursor.execute(
                    """INSERT INTO resume_data(
                        candidate_name,
                        job_role,
                        match_percentage,
                        missing_skills,
                        suggestion
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "",
                        job,
                        0,
                        "",
                        response.text
                    )
                )

                conn.commit()
                conn.close()

                st.success("Result saved to database")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
