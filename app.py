"""Search engine as a Flask app."""

import os
from flask import Flask, request, render_template, redirect, url_for, Response
from searcher import extended_search
from whoosh.index import open_dir

app = Flask(__name__)


@app.route("/")
def index() -> Response:
    """Define index route and redirect to /home.

    Returns:
        Response: redirect to /home

    """
    return redirect(url_for("home"))


@app.route("/home")
def home():
    """Process home page request by returning the home page template.

    Returns:
        str: rendered home page

    """
    return render_template("start.html")


@app.route("/search")
def search():
    """Look for the query in the index and return its results.

    Returns:
        str: rendered html page

    """
    index_path = os.path.join(app.root_path, "indexdir")
    ix = open_dir(index_path)
    query = request.args["q"]
    r, corrected = extended_search(query, ix)
    return render_template("search.html", results=r, q=query, corrected=corrected)
