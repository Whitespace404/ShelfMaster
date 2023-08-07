from shelfmaster import app
from flask import render_template, redirect, url_for, flash
from . import forms

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    form = forms.BorrowForm()

    if form.validate_on_submit():
        flash("Book borrowed successfully.")
        return redirect(url_for("home"))
    return render_template("borrow.html", form=form)


@app.route("/return", methods=["GET", "POST"])
def return_():
    return render_template("return.html")


@app.route("/success")
def success():
    return render_template("success.html")