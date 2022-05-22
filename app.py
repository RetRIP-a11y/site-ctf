import os
from flask import Flask, render_template, request, session, Blueprint, url_for, redirect, sessions
import sqlite3
import hashlib
from datetime import timedelta
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config ['portnow_session_lifetime'] = timedelta (days = 365)
con = sqlite3.connect('static/CTF-DB.db', check_same_thread=False)
cur = con.cursor()


def content(folder):
    task = []
    tree = os.listdir(folder)
    for i in sorted(tree):
        with open(folder + i + '/task', 'r') as target:
            text = target.read()
        category = text.split('\n')[0].split(':')[1]
        name = text.split('\n')[1].split(':')[1]
        description = text.split('\n')[2].split(':')[1]
        hint1 = hint2 = hint3 = ''
        try:
            hint1 = text.split('\n')[3].split(':')[1]
            hint2 = text.split('\n')[4].split(':')[1]
            hint3 = text.split('\n')[5].split(':')[1]
        except:
            pass
        task.append([i, category, name, description, hint1, hint2, hint3])
    return task


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=('GET', 'POST'))
def auth():
    login = ''
    password = ''
    if request.method == 'POST':
        login = request.form['login']
        password = hashlib.md5(request.form['pass'].encode()).hexdigest()
        sql = "SELECT id, role FROM users WHERE login = '" + login + "' AND password = '" + str(password) + "'"
        cur.execute(sql)
        res = cur.fetchall()
        if res != []:
            sql = "SELECT auth FROM users WHERE id = '" + str(res[0][0]) + "'"
            cur.execute(sql)
            auth = cur.fetchall()
            if auth[0][0] == 'False':
                session['id'] = res[0][0]
                session['role'] = res[0][1]
                session['auth'] = True
                session.permanent = True
                sql = "UPDATE users SET auth = 'True' "
                cur.execute(sql)
                con.commit()
                return redirect(url_for('ctf'))
            else:
                return render_template('auth.html', msg='Уже авторизован')
        else:
            return render_template('auth.html', msg='не праильные логин или пароль')
    else:
        if 'auth' in session:
            return redirect(url_for('ctf'))
        else:
            return render_template('auth.html')


@app.route('/<folder>')
def task(folder):
    try:
        task = content('task/'+folder+'/')
        return render_template('render.html', task=task)
    except:
        return render_template('404.html'), 404


@app.route('/check', methods=('GET', 'POST'))
def check():
    if request.method == 'POST':
        task = request.form['btn']
        task = task.split(',')
        category = task[1].lower()
        folder = task[0]
        flag = request.form['flag']
        with open('task/'+category+'/'+folder+'/task') as text:
            text = text.read()
        right_flag = text.split('\n')[6].split(':')[1]
        if right_flag == flag:
            return 'SUCCES'
        else:
            return 'ERROR'


@app.route('/ctf')
def ctf():
    if 'auth' in session:
        task = content('task/ctf/')
        return render_template('ctf.html', task=task)
    else:
        return redirect('/')


@app.route('/users')
def users():
    if 'auth' in session and session['role'] == 'root':
        sql = "SELECT id, login, role FROM users"
        cur.execute(sql)
        res = cur.fetchall()
        return render_template('users.html', content=res)
    else:
        return redirect('/')

@app.route('/create_user', methods=('GET', 'POST'))
def create_user():
    if 'auth' in session and session['role'] == 'root':
        new_login = "'" + request.form['new_login'] + "'"
        new_pass = "'" + hashlib.md5(request.form['new_pass'].encode()).hexdigest() + "'"
        new_role = "'" + request.form['new_role'] + "'"
        sql = "INSERT INTO users(login, password, role) VALUES("+new_login+', '+new_pass+', '+new_role+");"
        cur.execute(sql)
        con.commit()
        return redirect(url_for('users'))
    else:
        return redirect('/')


@app.route('/delete_user', methods=('GET', 'POST'))
def delete_user():
    if 'auth' in session and session['role'] == 'root':
        id_delete = "'" + request.form['id_delete'] + "'"
        sql = "DELETE FROM users WHERE id = " + id_delete
        cur.execute(sql)
        con.commit()
        return redirect(url_for('users'))
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    sql = "UPDATE users SET auth = 'False' "
    cur.execute(sql)
    con.commit()
    session.clear()
    return redirect('/')

@app.route('/robots.txt')
def robots():
    return '<p style="font-size: 3rem">/s3cr3t f01d3r/<p>'

@app.route('/s3cr3t f01d3r/')
def secret():
    return '<p style="font-size: 3rem">vi_ctf{azat_sosat}</p>'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=1234)
