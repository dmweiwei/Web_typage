import logging.config
import os

from flask import Flask, render_template, redirect, request, jsonify, abort, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from src.utils import allowed_file, process, tf_idf_transform, prediction
from src.settings import ALLOWED_EXTENSIONS
from config import Config

version = __import__('version').__version__
logging.config.fileConfig('logging.ini')
logger = logging.getLogger('main')

### ------------------------------- Programme commence ici-------------------------###
logger.info(">>> Web_typage - v{} <<<".format(version))
logger.info(">>> Debut du programme <<<")

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# page pour télécharger le fichier textuel
@app.route('/')
def upload_test():
    return render_template('upload.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    f = request.files['myfile']
    filename = secure_filename(f.filename)
    if filename != '':
        # Vérifier si l'extention est dans la liste autorisée
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            # abort(400)
            return error()
        else:
            try:
                contenu = f.read()
                # contenu = contenu.strip("\n").decode("utf-16")
                contenu = contenu.decode('cp1252')
                contenu_preprocessed = process(contenu)
                contenu_tfidf = tf_idf_transform([contenu_preprocessed])
                top3typage = prediction(contenu_tfidf)

                top1name, top1pourcentage = top3typage[0][0], top3typage[0][1]
                top2name, top2pourcentage = top3typage[1][0], top3typage[1][1]
                top3name, top3pourcentage = top3typage[2][0], top3typage[2][1]

                logger.info("Succès de typer le document : {}".format(filename))
                return render_template('result.html', top1name=top1name, top1pourcentage=top1pourcentage,
                                       top2name=top2name, top2pourcentage=top2pourcentage,
                                       top3name=top3name, top3pourcentage=top3pourcentage)
            except Exception as e:
                message = "Erreur lors de typer le document : {0}. Erreur : {1}".format(filename, e)
                logger.error(message)
                return e, error()
    else:
        # abort(400)
        return error()


logger.info(">>> Fin du programme <<<")

if __name__ == '__main__':
    app.run(debug=True)
