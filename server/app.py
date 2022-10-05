from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route("/")
def hello_world():
    with open('status.txt') as file:
        status = str(file.read())
    return render_template("index.html", value=status)

@app.route("/get_status")
def get_status():
    with open('status.txt') as file:
        status = file.read()
    return status

@app.route("/set_on", methods = ['POST'])
def set_on():
    with open('status.txt', 'w') as file:
        file.write('ON')
    return redirect("/")

@app.route("/set_off", methods = ['POST'])
def set_off():
    with open('status.txt', 'w') as file:
        file.write('OFF')
    return redirect("/")
