# from email.mime import image
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import DevelopmentConfig
from flask import render_template, request, url_for, flash, g
from flask import session
from flask import send_from_directory
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)

path = 'packageUsers'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

### MODELO
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(40),unique=True)
    password = db.Column(db.String(255))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    folder_user = db.relationship('Folder_User')
    
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = self.create_password(password)
    
    def create_password(self,password):
        return generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password, password)

class Folder_User(db.Model):
    __tablename__='folder_user'
    id = db.Column(db.Integer, primary_key=True)
    namefolder = db.Column(db.String(255))
    imagefile = db.Column(db.String(255))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    folder_cap = db.relationship('Folder_Cap')
    
    def __init__(self,namefolder,imagefile,user_id):
        self.namefolder = namefolder
        self.imagefile = imagefile
        self.user_id = user_id

class Folder_Cap(db.Model):
    __tablename__='folder_cap'
    id = db.Column(db.Integer, primary_key=True)
    namecapitulo = db.Column(db.String(255))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    folder_user_id = db.Column(db.Integer, db.ForeignKey('folder_user.id'))
    image_cap = db.relationship('Image_Cap')
    
    def __init__(self,namecapitulo,folder_user_id):
        self.namecapitulo = namecapitulo
        self.folder_user_id = folder_user_id

class Image_Cap(db.Model):
    __tablename__='image_cap'
    id = db.Column(db.Integer, primary_key=True)
    imagecapname = db.Column(db.String(255))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    folder_cap_id = db.Column(db.Integer, db.ForeignKey('folder_cap.id'))
    
    def __init__(self,imagecapname,folder_cap_id):
        self.imagecapname = imagecapname
        self.folder_cap_id = folder_cap_id
###FIN MODELO

###ROUTES
@app.before_request
def before_login():
    g.user = session.get('email') 
    if g.user is None and request.endpoint in ['logout','update','userdata','folder','dashboard']:
        return redirect(url_for('index'))
    elif g.user is not None and request.endpoint in ['login','register']:
        return redirect(url_for('index'))
        
@app.after_request
def after_login(response):
    return response

@app.route('/')
def index():
    folder_user = Folder_User.query.all()
    if folder_user is not None:
        return render_template('lista/listaIndex.html',folderUser = folder_user,path=path)
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    usuario = User.query.filter_by(email=g.user).first()
    folder_user = Folder_User.query.filter_by(user_id=usuario.id).all()
    if folder_user is not None:
        return render_template('lista/dashboard.html',folderUser = folder_user,path=path)
    print(folder_user)
    return render_template('index.html')

#BUSCAR EN TABLA IMAGE

@app.route('/view/<namefolder>')
def mostrarcapitulos(namefolder):
    # https://stackoverflow.com/questions/27900018/flask-sqlalchemy-query-join-relational-tables
    vercapitulos = Folder_User.query.join(Folder_Cap, Folder_Cap.folder_user_id==Folder_User.id).add_columns(Folder_Cap.namecapitulo,Folder_User.namefolder).filter(Folder_User.namefolder==namefolder).all()
    return render_template('lista/listacapitulo.html',vercapitulos=vercapitulos)

@app.route('/view/<namefolder>/<capitulo>')
def mostrarimagenes(namefolder,capitulo):
    ga = Folder_User.query.join(Folder_Cap, Folder_Cap.folder_user_id==Folder_User.id).add_columns(Folder_Cap.id,Folder_Cap.namecapitulo,Folder_User.namefolder).filter(Folder_User.namefolder==namefolder).all()
    for i in ga:
        if i.namecapitulo== capitulo:
            imagecap = Image_Cap.query.filter_by(folder_cap_id=i.id).all()
            return render_template('lista/imgcapitulo.html',imagecap=imagecap,path=path,info=i)

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            session['email'] = email
            flash(f'Usuario {user.username} logeado correctamente')
            return redirect(url_for('index'))
        else:
            flash(f'Contrase??a o correo no validos')
    return render_template('login/login.html')

@app.route('/logout')
def logout():
    if g.user:
        session.pop('email')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        V_user = User.query.filter_by(email=email).first()
        if V_user is None:
            newUser = User(userName,email,password)
            db.session.add(newUser)
            db.session.commit()
            session['email'] = email
            flash(f'usuario {email} creado')
            return redirect(url_for('index'))
        else:
            flash('El usuario ya existe')
    return render_template('login/register.html')

# @app.route('/deleteUser/<int:id>')
# def delete(id):
#     usuario = db.session.query(User).get(id)
#     # usuario = User.query.get(id)
#     if g.user == usuario.email:
#         session.pop('email')
#     db.session.delete(usuario)
#     db.session.commit()
#     return redirect(url_for('index'))

@app.route('/update',methods=['POST','GET'])
def update():
    usuario = User.query.filter_by(email=g.user).first()
    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.email = request.form['email']
        db.session.commit()
        if g.user != usuario.email:
            session['email'] = usuario.email
        return redirect(url_for('index'))
    return render_template('login/update.html',usuario=usuario)

@app.route('/userdata')
def dataUser():
    usuario = User.query.filter_by(email=g.user).first()
    return render_template('login/userData.html',usuario=usuario)

@app.route('/folder',methods=['POST','GET'])
def folder():
    # https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
    if request.method == 'POST':
        usuario = User.query.filter_by(email=g.user).first()
        namefolder = request.form['namefolder']
        foto = request.files['imgfolder']
        if foto.filename !='' and allowed_file(foto.filename):
            os.mkdir(f'{path}/{namefolder}')
            filename = secure_filename(foto.filename)
            portada = f'portada{filename}'
            foto.save(f'{path}/{namefolder}/{portada}')
            folder = Folder_User(namefolder,portada,usuario.id)
            db.session.add(folder)
            db.session.commit()
        else:
            flash('campo no llenado o incorrecto')
    return render_template('image/folder.html')

@app.route('/capitulo/<int:id>',methods=['POST','GET'])
def capitulo(id):
    cap = Folder_User.query.join(Folder_Cap, Folder_Cap.folder_user_id==Folder_User.id).add_columns(Folder_Cap.namecapitulo,Folder_User.namefolder).filter(Folder_User.id==id).all()
    folder = Folder_User.query.filter_by(id=id).first()
    # https://roytuts.com/upload-and-display-multiple-images-using-python-and-flask/
    if request.method == 'POST':
        namecap = request.form['namecapitulo']
        foto = request.files.getlist('imgcap')
        if namecap !='':
            folder_cap = Folder_Cap(namecap,id)
            db.session.add(folder_cap)
            db.session.commit()
            os.mkdir(f'{path}/{folder.namefolder}/{namecap}')
            registercap = Folder_User.query.join(Folder_Cap, Folder_Cap.folder_user_id==Folder_User.id).add_columns(Folder_Cap.id,Folder_User.namefolder,Folder_Cap.namecapitulo).filter(Folder_User.id==id).all()
            for j in registercap:
                if namecap == j.namecapitulo:
                    for i in foto:
                        if i and allowed_file(i.filename):
                            filename = secure_filename(i.filename)
                            i.save(f'{path}/{folder.namefolder}/{namecap}/{filename}')
                            imgcap = Image_Cap(filename,j.id)
                            db.session.add(imgcap)
                            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('capitulos/capitulo.html',id=id, cap=cap)

@app.route('/<path>/<namefolder>/<name>')
def directoriIndex(path,namefolder,name):
    return send_from_directory(f'{path}/{namefolder}',name)
################################
@app.route('/<path>/<namefolder>/<nameCapitulo>/<nameImage>')
def directoriCap(path,namefolder,nameCapitulo,nameImage):
    return send_from_directory(f'{path}/{namefolder}/{nameCapitulo}',nameImage)
###FIN ROUTES

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()