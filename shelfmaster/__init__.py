from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = "28679ae72d9d4c7b0e93b1db218426a6"

from shelfmaster import routes