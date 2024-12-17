from flask import Flask, request, render_template, redirect, url_for
from crawler import extended_search
from whoosh.index import open_dir
import os
app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    return render_template('start.html')

@app.route("/search")
def search():
    ix = open_dir("indexdir")
    w = request.args['q']
    r = extended_search(w, ix)
    print(f"{len(r)} elements found")
    for res in r:
        print(r)
    return render_template('search.html', results=r)
