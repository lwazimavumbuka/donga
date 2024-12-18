from flask import Flask, render_template

dongaapp = Flask(__name__)

@dongaapp.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':
    dongaapp.run(debug=True)