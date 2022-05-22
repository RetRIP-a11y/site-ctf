import os
import json
from flask import Flask, render_template
import glob


app = Flask(__name__)

def content(folder):
    tree = os.listdir(folder)
    for i in sorted(tree):
        with open(folder + i + '/task', 'r') as target:
            text = target.read()
        name = text.split('\n')[0].split(':')[1]
        description = text.split('\n')[1].split(':')[1]
        hint1 = hint2 = hint3 = ''
        try:
            hint1 = text.split('\n')[2].split(':')[1]
            hint2 = text.split('\n')[3].split(':')[1]
            hint3 = text.split('\n')[4].split(':')[1]
        except:
            pass
        # task.append({'id': i, 'name': name, 'description': description, 'hint1': hint1, 'hint2': hint2, 'hint3': hint3})
        task.append([i, name, description, hint1, hint2, hint3])

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/web')
def web():
    task = []

    return render_template('web.html', task=task)

@app.route('/pwn')
def pwn():
    task = [['0', 'firstPwn', 'Твой первый PWN', 'туут подсказка'], ['1', 'secondPwn', 'Ну ты уже понял что делать', 'hint1']]
    return render_template('pwn.html', task=task)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=1234)