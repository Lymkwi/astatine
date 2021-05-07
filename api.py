"""API module"""
import os
import random
from pathlib import Path
from requests_toolbelt import MultipartEncoder
from flask import Flask, request, Response, render_template

# from ml_models.yolov5 import detect as detection
# from ml_models.yolov5 import train

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

from ml_models.astatine import main as load
from data.download import download_data

# Download missing datasets (~400Mo)
download_data()

api = Flask(__name__)

api.config['UPLOAD_EXTENSIONS'] = ['png', 'jpg', 'jpeg', 'gif']
api.config['UPLOAD_FOLDER'] = 'received'

# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Example request :  curl -X POST -F "send_result=true|false" -F image=@image.jpg (-o output.jpg/-i) host:port
# https://medium.com/@pemagrg/build-a-web-app-using-pythons-flask-for-beginners-f28315256893
@api.route('/')
def home():
    return render_template('index.html')

@api.route('/<module>', methods=['POST'])
def module_caption(module):
    if module not in ['yolo', 'captioning']:
        return "Module not found.", 404
    if 'image' not in request.files:
        return "ERROR", 500

    file = request.files['image']

    ext = file.filename.split('.')[-1]

    # Check if the upload folder exists
    upload_path = Path(f"{api.config['UPLOAD_FOLDER']}")
    if not upload_path.exists():
        upload_path.mkdir()

    id = random.randint(0, 1000)
    while Path(f"{api.config['UPLOAD_FOLDER']}/tmp_{id}.{ext}").is_file():
        id = random.randint(0, 1000)

    path = os.path.join(api.config['UPLOAD_FOLDER'], f'tmp_{id}.{ext}')

    if file:
        file.save(path)
        caption = load.main(path, module)

        resultFile = path

        responseFields = {'caption': caption}
        
        if module == 'yolo' and request.form['send_result'] == 'true':
            responseFields['result'] = (f'preview.{ext}', open(resultFile, 'rb'), file.content_type)

        os.remove(path)
        m = MultipartEncoder(fields=responseFields)
        return Response(m.to_string(), mimetype=m.content_type), 200

if __name__ == '__main__':
    api.run(host='0.0.0.0', debug=True, port=6969)#, ssl_context=context)
