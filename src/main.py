import logging.config
import os

from flask import Flask, render_template, redirect, request, abort, url_for, flash, session, g
from werkzeug.utils import secure_filename

from src.models import users
from src.utils import process, tf_idf_transform, prediction, get_typage_alpha, get_typage_num
from src.settings import ALLOWED_EXTENSIONS

version = __import__('version').__version__
logging.config.fileConfig('logging.ini')
logger = logging.getLogger('main')

# ------------------------------- Programme commence ici------------------------- #
logger.info(">>> Web_typage - v{} <<<".format(version))
logger.info(">>> Debut du programme <<<")

app = Flask(__name__)
app.secret_key = 'TheKeyIKnow'


@app.before_request
def before_request():
    if 'user_id' not in session and request.endpoint is None:
        return redirect(url_for('login'))
    elif 'user_id' in session and request.endpoint is None:
        user = [u for u in users if u.id == session['user_id']][0]
        g.user = user
        return redirect(url_for('upload'))


# Page pour s'authentifier
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form.get('username')
        password = request.form.get('password')

        for u in users:
            if u.username == username:
                user = u
                if user and user.password == password:
                    session['user_id'] = user.id
                    return redirect(url_for('upload'))

                # flash("Mot de passe incorrect")
                # return redirect(url_for('login'))
            flash("Nom de l'utilisateur ou mot de passe incorrect")
            return redirect(url_for('login'))
    return render_template('login.html')


# page pour télécharger le fichier textuel
@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    message1 = ""
    message2 = ""
    f = request.files['myfile']
    filename = secure_filename(f.filename)
    if filename != '':
        # Vérifier si l'extention est dans la liste autorisée
        file_ext = os.path.splitext(filename)[1]
        typage_du_document_num = get_typage_num(filename)
        typage_du_document_alpha = get_typage_alpha(typage_du_document_num)
        if file_ext not in ALLOWED_EXTENSIONS:
            # abort(400)
            flash("L'extention n'est pas acceptable")
            return render_template('api/upload')
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

                if typage_du_document_alpha == top1name:
                    message1 = "Bravo! La prédiction est correcte!"
                else:
                    message2 = "Dommage, le typage correct est :\n{}".format(typage_du_document_alpha)

                logger.info("Succès de typer le document : {}".format(filename))
                return render_template('result.html', top1name=top1name, top1pourcentage=top1pourcentage,
                                       top2name=top2name, top2pourcentage=top2pourcentage,
                                       top3name=top3name, top3pourcentage=top3pourcentage,
                                       message1=message1, message2=message2)
            except Exception as e:
                message = "Erreur lors de typer le document : {0}. Erreur : {1}".format(filename, e)
                logger.error(message)
                return e, error()
    else:
        # abort(400)
        return error()


if __name__ == '__main__':
    logger.info(">>> Début du programme <<<")
    app.run(debug=True, port=2020)
    logger.info(">>> Fin du programme <<<")

