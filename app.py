#module1
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
upload_file=st.file_uploader("upload your resume(PDF)",type=["pdf"])

job=st.text_area("Enter job Description:\n")

text=""
images=[]
if upload_file is not None:
     pdf_bytes=upload_file.read()

     doc=fitz.open(stream=pdf_bytes, filetype="pdf")

     for page in doc:
         text+=page.get_text()
         pix=page.get_pixmap(matrix=fitz.Matrix(2,2))
         img= Image.open(io.BytesIO(pix.tobytes("png")))
         images.append(img)
     st.success("Resume uploaded successfully")
     st.write(text[:1000])


#module6
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("api_key")) 
model=genai.GenerativeModel("gemini-2.5-flash")

if upload_file is not None:
     if st.button("Analyze resume"):
       
       prompt= f""" you are an expert ATC(Applicant Tracking System).
               Analyze the following resumeagains the given job description.

               resume:
               {text}
               job description:
               {job}
               Return your response in exactly this format:

               1.Match percentage:

               2.Missing skills
                -skills1
                -skills2
                -skills3

               3.Matching skills:
                -skills1
                -skills2
                -skills3

               4.strengths:
                -point1
                 point2

               5.Weakness:
                 point1
                 point2

               6.Suggestions
                 point1
                 point2

                 Dont make it too large only give essential things in short and professional """


       if text.strip():
           response=model.generate_content(prompt+ "\n\nResume:\n"+text)
       else:
           response=model.generate_content([prompt, images[0]])

       st.write(response.text)

#module7
       
       conn=sq.connect("resume.db")
       cursor=conn.cursor()
     
       cursor.execute("""INSERT INTO resume_data(
                    candidate_name,
                    job_role,
                    match_percentage,
                    missing_skills,
                    suggestion
                    )
                    VALUES(?,?,?,?,?)
                    """,
                    ("",
                    job,
                    0,
                    "",
                    response.text
                    ))
       conn.commit()
       conn.close()
       st.success("Result saved to database")

