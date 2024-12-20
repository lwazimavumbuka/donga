from flask import Flask, render_template, request, jsonify
from requests import post, get
import requests
from moviepy import VideoFileClip
import os
import whisper

dongaapp = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/Lenovo/Documents/Uploads/'
dongaapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
files = []

@dongaapp.route("/")
def home():
    files.clear()
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

    #clip = VideoFileClip('C:/Users/Lenovo/Documents/videoplayback.mp4')
    #clip.audio.write_audiofile(f"{dongaapp.config['UPLOAD_FOLDER']}audio.mp3")
    #print(file_path)
    return jsonify(files)

@dongaapp.route("/generate_audio", methods=['POST'])
def generate_audio():
    filepath = request.json

    clip = VideoFileClip(filepath)
    clip.audio.write_audiofile(f"{dongaapp.config['UPLOAD_FOLDER']}audio.mp3")

    model = whisper.load_model("tiny")
    result = model.transcribe(f"{dongaapp.config['UPLOAD_FOLDER']}audio.mp3")
    print(result['text'])

    print(filepath)
    return ''

if __name__ == '__main__':
    dongaapp.run(debug=True)