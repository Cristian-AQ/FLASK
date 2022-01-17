# para crear rutas personalizadas
from flask import Blueprint
from flask import render_template, request, url_for, flash, g
from flask import session
from werkzeug.utils import redirect
from models.User import User
from utils.db import db

logeo = Blueprint('login',__name__)

@logeo.before_app_request
def before_request_login():
    g.user = session.get('email') 
    if g.user is None and request.endpoint in ['login.static','login.logout','login.index']:
        return redirect(url_for('login.register'))
    elif g.user is not None and request.endpoint in ['login.login','login.register','login.static']:
        return redirect(url_for('login.index'))
        
@logeo.after_app_request
def after_request_login(response):
    return response

@logeo.route('/')
def index():
    usuarios = User.query.all()
    return render_template('lista/lista.html',listado = usuarios)

@logeo.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            session['email'] = email
            flash(f'Usuario {user.username} logeado correctamente')
            return redirect(url_for('login.index'))
        else:
            flash(f'Contraseña o correo no validos')
    return render_template('login/login.html')

@logeo.route('/logout')
def logout():
    if g.user:
        session.pop('email')
    return redirect(url_for('login.login'))

@logeo.route('/registerUser', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        V_user = User.query.filter_by(email=email).first()
        if V_user is None:
            newUser = User(userName,email,password)
            db.session.add(newUser)
            db.session.commit()
            session['email'] = email
            flash(f'usuario {email} creado')
            return redirect(url_for('login.index'))
        else:
            flash('El usuario ya existe')
    return render_template('login/register.html')

@logeo.route('/deleteUser/<int:id>')
def delete(id):
    usuario = db.session.query(User).get(id)
    # usuario = User.query.get(id)
    if g.user == usuario.email:
        session.pop('email')
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('login.index'))

@logeo.route('/updateUser/<int:id>',methods=['POST','GET'])
def update(id):
    usuario = db.session.query(User).get(id)
    if request.method == 'POST':
        usuario.username = request.form['userName']
        usuario.email = request.form['email']
        db.session.commit()
        return redirect(url_for('login.index'))
    return render_template('login/update.html',usuario=usuario)