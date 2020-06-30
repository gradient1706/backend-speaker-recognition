from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    return 'Hello! Welcome to Backend Speaker Recognition'
    

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')