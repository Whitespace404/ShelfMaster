from shelfmaster import app
from flask import render_template

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow")
def borrow():
    return render_template("borrow.html")


@app.route("/return")
def return_():
    return render_template("return.html")
