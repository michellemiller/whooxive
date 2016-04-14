from flask import Flask
from flask import request
from flask import render_template
from sklearn.externals import joblib
import json


# from flask import send_static_file
app = Flask(__name__)

clf_journal = joblib.load('svm_journal.pkl')
clf_category = joblib.load('svm_category.pkl')

journals = ['PRL', 'Nature']

@app.route("/")
def hello():
    return render_template("abstract_predictor.html")
    # return send_static_file("test.html")

@app.route('/svm', methods=['POST'])
def svm_category():
    abstract = str(request.form['abstract'])

    journal_predict = journals[clf_journal.predict([abstract])]
    category_predict = clf_category.predict([abstract])

    return json.dumps({'status': 'OK',
                       'abstract': abstract.lower(),
                       'journal': journal_predict,
                       'category': ', '.join(category_predict[0])})

if __name__ == "__main__":
    app.run(debug=True)