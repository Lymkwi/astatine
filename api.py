"""API module"""
import os
import random
from pathlib import Path
from threading import Lock
from requests_toolbelt import MultipartEncoder
from flask import Flask, request, Response, render_template

# Uncomment the following lines if you want to use HTTPS

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

# Download missing datasets (~400Mo)
from data.download import download_data
download_data()

from ml_models.astatine import main as load

api = Flask(__name__)

api.config.from_pyfile('config.py')

requestCounter = 0
requestLock = Lock()

# Example request :  curl -X POST -F "send_result=true|false" -F image=@image.jpg (-o output.jpg/-i) host:port
# https://medium.com/@pemagrg/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
@api.route('/')
def home():
    return render_template('index.html')

@api.route('/<module>', methods=['POST'])
def module_caption(module):
    # If the endpoint requested doesn't correspond to any existing module
    if module not in ['yolo', 'resnet']:
        return "ERROR: Module not found.", 404
    # If the request doesn't include any image
    if 'image' not in request.files:
        return "ERROR: No file sent.", 400

    file = request.files['image']

    ext = file.filename.split('.')[-1].lower()
    # If the file doesn't have the right extension
    if ext not in api.config['UPLOAD_EXTENSIONS']:
        return "ERROR: Unauthorized image format", 400

    # Check if the upload folder exists
    upload_path = Path(f"{api.config['UPLOAD_FOLDER']}")
    if not upload_path.exists():
        upload_path.mkdir()

    global requestCounter
    requestLock.acquire()
    if requestCounter >= api.config['MAX_CONCURRENT_REQUESTS']:
        requestLock.release()
        return "Too many requests", 429
    requestCounter += 1
    requestLock.release()

    id = random.randint(0, 1000)
    while Path(f"{api.config['UPLOAD_FOLDER']}/tmp_{id}.{ext}").is_file():
        id = random.randint(0, 1000)

    path = os.path.join(api.config['UPLOAD_FOLDER'], f'tmp_{id}.{ext}')

    if file:
        file.save(path)
        caption = load.main(path, module)

        requestLock.acquire()
        requestCounter -= 1
        requestLock.release()

        resultFile = path

        responseFields = {'caption': caption}

        if module == 'yolo' and request.form['send_result'] == 'true':
            with open(resultFile, 'rb') as f:
                responseFields['result'] = (f'preview.{ext}', f.read(), file.content_type)

        os.remove(path)
        m = MultipartEncoder(fields=responseFields)
        return Response(m.to_string(), mimetype=m.content_type), 200

if __name__ == '__main__':
    api.run(host='0.0.0.0', debug=True, port=6969)#, ssl_context=context)
