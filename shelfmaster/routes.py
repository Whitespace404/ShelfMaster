from shelfmaster import app

@app.route("/")
def home():
    return "<hr>"