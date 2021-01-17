import logging.config
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import FrenchStemmer
from nltk.corpus import stopwords
import joblib
from itertools import islice
import csv



logging.config.fileConfig('logging.ini')
logger = logging.getLogger('utils')

### ------------------ Initialisation --------------------------------###
tfidf_word = joblib.load("tfidf_word.sav")
model_svc = joblib.load("svc_for_web_typage.sav")


def allowed_file(filename):
    """
    Fonction pour vérifier si le fichier téléchargé est autorisé
    :param filename: le nom du fichier
    :return: true or false
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def process(input_text):
    """
    Nettoyer le contenu brut
    :param input_text: le contenu brut
    :return: le contenu nettoyé
    """
    try:
        # Initialiser le tokenizer d'une expression régulière
        tokenizer = RegexpTokenizer(r'\w+')
        # Initialiser la liste de stop-words
        stop_words = stopwords.words('french')
        # Tokenize input (format string)
        tokens = tokenizer.tokenize(input_text.lower())
        # Supprimer les stop words
        tokens = [x for x in tokens if x not in stop_words]
        # Initialiser le stemmer
        stemmer = FrenchStemmer()
        # Stemmer les mots tokenizés
        tokens_stemmed = [stemmer.stem(x) for x in tokens]
        return " ".join(tokens_stemmed)
    except Exception as e:
        message = "Erreur lors du preprocessing. Erreur : {}".format(e)
        logger.error(message)


def tf_idf_transform(content):
    """
    Vectoriser le contenu (en string) avec tf-idf déjà entraîné
    :param content: le contenu à vectoriser
    :return: le contenu vectorisé
    """
    try:
        content_tfidf = tfidf_word.transform(content)
        return content_tfidf
    except Exception as e:
        message = "Erreur lors de la transformation du contenu en vecteur TF-IDF. Erreur : {}".format(e)
        logger.error(message)


def prediction(content_tfidf):
    """
    Prédire le typage et donner la probabilité de chaque classe
    :param content_tfidf: le contenu vectorisé
    :return: la prédiction et le predict proba
    """
    try:
        # prediction = model_svc.predict(content_tfidf)
        predict_proba = model_svc.predict_proba(content_tfidf)
        predict_proba_list = list(predict_proba[0])
        targets = list(model_svc.classes_)
        dico_proba = {targets[i]: round(predict_proba_list[i]*100,2) for i in range(len(predict_proba_list))}
        dico_proba_ordered = {k: v for k, v in sorted(dico_proba.items(), key=lambda item: item[1], reverse=True)}
        top3_typage = list(islice(dico_proba_ordered.items(), 3))
        return top3_typage
    except Exception as e:
        message = "Erreur lors de la prediction. Erreur : {}".format(e)
        logger.error(message)


def get_typage_alpha(typage_num):
    """
    Fonction de trouver le typage alphabétique à partir du typage numérique
    :param typage_num:
    :return:
    """
    with open('code_typage_commun.csv', 'r') as file:
        reader = csv.reader(file, delimiter = ';')
        for row in reader:
            if typage_num in row:
                return row[1]

