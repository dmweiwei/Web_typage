import logging.config
from flask import Flask, render_template, redirect, request, jsonify
from src.utils import allowed_file, process, tf_idf_transform, prediction

version = __import__('version').__version__
logging.config.fileConfig('logging.ini')
logger = logging.getLogger('main')

### ------------------------------- Programme commence ici-------------------------###
logger.info(">>> Web_typage - v{} <<<".format(version))
logger.info(">>> Debut du programme <<<")

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 具有上传功能的页面
@app.route('/')
def upload_test():
    return render_template('upload.html')


@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    f = request.files['myfile']
    # Vérifier si l'extention est dans la liste autorisée
    if f and allowed_file(f.filename):
        contenu = f.read()
        # contenu = contenu.strip("\n").decode("utf-16")
        contenu = contenu.decode('cp1252')
        contenu_preprocessed = process(contenu)
        contenu_tfidf = tf_idf_transform([contenu_preprocessed])
        top3typage = prediction(contenu_tfidf)

        top1name, top1pourcentage = top3typage[0][0], str(top3typage[0][1]) + "%"
        top2name, top2pourcentage = top3typage[1][0], str(top3typage[1][1]) + "%"
        top3name, top3pourcentage = top3typage[2][0], str(top3typage[2][1]) + "%"

        return render_template('result.html', top1name=top1name, top1pourcentage=top1pourcentage,
                               top2name=top2name, top2pourcentage=top2pourcentage,
                               top3name=top3name, top3pourcentage=top3pourcentage)
        # return jsonify({"errno": 0, "errmsg": prediction_typage})
    else:
        return "Erreur", redirect('upload.html')


logger.info(">>> Fin du programme <<<")


if __name__ == '__main__':
    app.run(debug=True)
