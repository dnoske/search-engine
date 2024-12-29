"""Search engine as a Flask app."""

from flask import Flask, request, render_template, redirect, url_for, Response
from crawler import extended_search
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
    ix = open_dir("indexdir")
    w = request.args["q"]
    r = extended_search(w, ix)
    print(f"{len(r)} elements found")
    for res in r:
        print(r)
    return render_template("search.html", results=r, q=w)
