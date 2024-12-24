from flask import Flask, render_template, request, jsonify
from requests import post, get
import requests
from moviepy import VideoFileClip
import os
import whisper
from concurrent.futures import ProcessPoolExecutor
import time
import google.generativeai as genai
import os
from fpdf import FPDF
from markdown import markdown
from weasyprint import HTML
from latex import build_pdf

dongaapp = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/Lenovo/Documents/Uploads/'
dongaapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
files = []
key = 'AIzaSyCWRIpZjIThwvrvAF6pddxsFCpT_44rsJA'

# Prompt
IDENTITY = '''
You are a highly focused, structured, and efficient note-taker 
who processes text transcripts into high-quality study notes. 
You are interested in extracting essential points, organizing 
content for clarity, and formatting information in an engaging 
and structured latex format. Your goal is to create concise, 
actionable, and easy-to-read notes that facilitate learning and revision.\n'''

STEPS = '''
STEPS:

1.Understand the Context:
-Identify the primary subject or topic of the transcript.
-Determine the purpose of the notes (e.g., exam preparation, topic overview, or summarizing a lecture).

Extract Key Points:
-Skim through the transcript for major themes, headings, or ideas.
-Focus on main arguments, supporting details, definitions, and examples.
-Highlight key terms, dates, formulas, or concepts for emphasis.
-Research the topics to add extra insight where necessary

2.Structure Your Notes:
-Use latex headers to organize the content into clear sections.
-Create bullet points for lists of related ideas or facts.
-Add subheadings to break down complex topics for better readability.

3.Summarize and Simplify:
-Rewrite long paragraphs into concise sentences or bullet points.
-Use plain, direct language and avoid unnecessary repetition.
-Ensure all content aligns with the study purpose.
-Use Formatting for Emphasis:

4.Highlight important terms in bold.
-Use italics for secondary details or clarifications.
-Include inline code syntax (e.g., `formula`) for equations or key terms.
-Use block quotes (>) for summarizing key arguments or quotes from the transcript.

5.Include Visual Aids where necessary:
-Suggest placeholders for diagrams, tables, or charts if applicable (e.g., [Insert Diagram: Topic Name]).
-Use tables in latex for comparisons or lists with multiple attributes.

6.Add Additional Features:
-Provide actionable items in checklists when relevant (e.g., - [ ] Study this further).
-Include a "Key Takeaways" section summarizing the transcript in 3–5 points.
-If applicable, include links to resources, references, or further reading.

7. Output Quality Control:
-Proofread the notes for accuracy and readability.
-Make sure notes are ready for immediate use without further edits.\n
\nNow write me notes from this text transcript remeber to write in latex. 
- Use the `article` document class.
- Set 1-inch margins on all sides using the `geometry` package.
- Use 12pt font size.
- Include proper sectioning with `\\section`, `\\ subsection`, and bullet points using `itemize` for clear structure.
- Maintain consistent spacing without unnecessary blank spaces or forced breaks (`\\vspace`, `\\newpage`, etc.).
- Add line spacing of 1.5x using the `setspace` package.
- Use `\\textbf{}` for bold text and `\\textit{}` for emphasis when necessary.
- Fill pages naturally without large empty spaces or uneven text distribution.
- Ensure the LaTeX compiles without errors or warnings.
- Ensure there is space between sections
Your response should be the notes written in latex code, your response should 
be raw latex code, nothing else, do not write anything else outside the latex code. 
Just respond with the text of the notes in latex code. Just respond with latex. Do not include this in the first line. Your response will be inserted on build_pdf() nethod of latex library python so make sure the code matches that : ```latex 
and this in the end: ```. Include only any of these: includes:\\documentclass, \\begin{ document },\\end{ document} 
Here is the text transcription to make notes of:\n
'''

@dongaapp.route("/")
def home():
    files.clear()
   # genai.configure(api_key="AIzaSyCWRIpZjIThwvrvAF6pddxsFCpT_44rsJA")
   # model = genai.GenerativeModel("gemini-2.0-flash-exp")
   # response = model.generate_content("Write me notes study notes on this prompt make sure you organise the notes in a good structure with headings, subheadings, definitions and bullets. These will be written to a pdf so make sure to use a good format. Write the notes in a markdown format. return the results only do not say anything else. here is the prompt:Explain Theory of relativity")
   # #print(response.text)
   # response_text = response.text
   # html_content = markdown(response_text)
   # HTML(string=html_content).write_pdf("notespdf")
    
   # pdf = FPDF()
   # pdf.add_page()
   # pdf.set_font('Arial', size=12)
   # pdf.multi_cell(0, 10, response_text)
   # pdf.output('notes.pdf')
    
    #pdf = build_pdf(latex_text)

    #output_filename = "outputnotes.pdf"
    #with open(output_filename, 'wb') as f:
   #     f.write(pdf.data) 
    return render_template('index.html')

@dongaapp.route("/display-file", methods=['POST'])
def displayfile():
    file = request.files['file']

    if 'file' not in request.files:
        print('No file found')

    file_path = f"{dongaapp.config['UPLOAD_FOLDER']}{file.filename}"
    file.save(file_path)
    file_name = file.filename

    filesize = round(os.path.getsize(file_path) / 1024, 2)


    if(filesize<1024):
        file_str = str(filesize)
        size = file_str + " KB"

        files.append({
            'name': file_name,
            'size': size,
            'path': file_path
        })
        print(size)
    else:
        filesize = round(filesize/(1024),2)
        file_str = str(filesize)
        size = file_str + " MB"

        files.append({
            'name': file_name,
            'size': size,
            'path': file_path
        })
        print(size)    

    return jsonify(files)

@dongaapp.route("/generate_audio", methods=['POST'])
def generate_audio():
    filepath = request.json

    clip = VideoFileClip(filepath)
    cliplen = int(clip.duration)-1
    chunk_len = 60
    chunks = []
    model_name = "tiny"

    start = time.time()
    for i in range(0, cliplen, chunk_len):
        end_time = min(i + chunk_len, cliplen)
        audio_clip = clip.subclipped(i, end_time)
        audio_clip.audio.write_audiofile(f"{dongaapp.config['UPLOAD_FOLDER']}chunk_{i // chunk_len}.mp3")
        chunk_path = os.path.join(dongaapp.config['UPLOAD_FOLDER'], f"chunk_{i // chunk_len}.mp3")
        chunks.append(chunk_path)
        
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(transcribe_chunks, chunks, [model_name] * len(chunks)))
    
    end = time.time()
    print("combining results....")
    print(end-start)
    transcript = "\n".join(results)

    #generating notes
    genai.configure(api_key="YOUR API KEY")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(f"${IDENTITY} ${STEPS} ${transcript}")
    response_text = response.text
    response_text = response_text.replace("```latex","")
    response_text = response_text.replace("```","")
    print(response_text)
    
    pdf = build_pdf(response_text)

    output_filename = "outputnotes.pdf"
    with open(output_filename, 'wb') as f:
        f.write(pdf.data)




    print(transcript)


    print(filepath)
    return ''

def transcribe_chunks(chunk_path, model_name="tiny"):
    model = whisper.load_model(model_name)
    result = model.transcribe(chunk_path)
    return result['text']
    

if __name__ == '__main__':
    dongaapp.run(debug=True)
