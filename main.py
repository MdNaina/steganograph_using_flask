from flask import Flask, redirect, url_for, render_template, request
import os
import steganography as sg
from PIL import Image

file_count = 1

def set_count():
    global file_count
    if file_count < 5:
        file_count+=1
        return file_count
    else:
        file_count = 0
        return file_count



app = Flask(__name__)

upload_folder = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = upload_folder


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/<file_type>')
def menu(file_type):
    return render_template('menu.html', file_type=file_type)


@app.route('/<file_type>/encode')
def encode(file_type):
    return render_template('encode.html', file_type=file_type)


@app.route('/<file_type>/encoding', methods = ["POST"])
def encoding(file_type):
    if request.method == "POST":
        if 'filename' not in request.files:
            return "there is no file in form"
        file = request.files['filename']
        msg = request.form['message']
        f_count = str(set_count())
        if file_type == "audio":
            path = os.path.join(app.config['UPLOAD_FOLDER'], f'audio/temp{f_count}.'+file.filename[-3:])
            file.save(path)
            download_path = sg.encode_audio(path, msg, f_count)
        elif file_type == "image":
            path = os.path.join(app.config['UPLOAD_FOLDER'], f'image/temp{f_count}.'+file.filename[-3:])
            file.save(path)
            download_path = sg.encode_image(path, msg, f_count)
        return render_template('download.html', file_path = download_path, file_type=file_type)

@app.route('/<file_type>/decode')
def decode(file_type):
    return render_template('decode.html', file_type=file_type)

@app.route('/<file_type>/decoding', methods = ["POST"])
def decoding(file_type):
    if request.method == "POST":
        if 'filename' not in request.files:
            return "there is no file in form"
        file = request.files['filename']
        f_count = str(set_count())
        if file_type == 'audio':
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio/temp.'+file.filename[-3:])
            file.save(path)
            msg = sg.decode_audio(path)
        elif file_type == "image":
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'image/temp.'+file.filename[-3:])
            file.save(path)
            msg = sg.decode_image(path)
        return render_template('decode_message.html', message = msg)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)



if __name__ == "__main__":
    app.run(debug=True)
