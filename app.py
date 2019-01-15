from io import StringIO

from flask import Flask, send_file, send_from_directory, request, redirect, Request, url_for
import json

from werkzeug.datastructures import ImmutableMultiDict

ALLOWED_EXTENSIONS = {"json", "jsn"}

app = Flask(__name__)
app.static_folder = "static"


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_extra_files(files: ImmutableMultiDict) -> dict:
    extra_files = {}
    print(files)
    for field_name, file in files.items():
        print(field_name, file)
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            extra_files[field_name] = StringIO(file.read())
    return extra_files


@app.route('/')
def index():
    return send_from_directory(app.static_folder+"/html", 'index.html')


@app.route("/loading")
def loading():
    pass


@app.route("/err")
def error():
    return send_from_directory(app.static_folder+"/html", "err.html")


@app.route('/go', methods=['POST'])
def go():
    if request.method == 'POST':
        print(request.files)
        extra_files = read_extra_files(request.files)
        for k, v in extra_files.items():
            print(k, v)
        return redirect(url_for("loading"))
    return redirect(url_for("error"))


if __name__ == '__main__':
    app.run()
