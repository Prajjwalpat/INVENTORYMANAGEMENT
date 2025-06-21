from flask import Flask
from main import bp
from logger import logger

app=Flask(__name__)
app.register_blueprint(bp)

if __name__=="__main__":
    app.run(debug=True)