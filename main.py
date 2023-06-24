from flask import Flask,flash,redirect , render_template, Response, Request, request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, login_manager,  LoginManager, current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors

import json



#databse connection
local_server = True
app = Flask(__name__)
app.config['SECRET_KET'] = 'dbproj2'
app.secret_key = "dbproj"

#login_manager, for getting user access
login_manager=LoginManager(app)
login_manager.login_view='login'


#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:@localhost/dbname"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/travel"
db=SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#--------------------------------------------------------------------------------------
#       DB MODELS
#--------------------------------------------------------------------------------------
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uname=db.Column(db.String(50),unique=True)
    email=db.Column(db.String(50))
    phone=db.Column(db.Integer)
    password=db.Column(db.String(10))
    city=db.Column(db.String(20))

class Destination(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    category=db.Column(db.String(50))
    name=db.Column(db.String(50))
    blog=db.Column(db.String(1000))
    country=db.Column(db.String(50))

class Food(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    resname=db.Column(db.String(50))
    locname=db.Column(db.String(50))
    cuisine=db.Column(db.String(50))
    blog=db.Column(db.String(50))

class Accomodation(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))
    locname=db.Column(db.String(50))
    budget=db.Column(db.Integer)
    review=db.Column(db.Integer)
    blog=db.Column(db.String(1000))


#--------------------------------------------------------------------------------------
#       BASIC ROUTES
#--------------------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/sfood')
def sfood():
    return render_template('food.html')

@app.route('/saccomodations')
def saccomodations():
    return render_template('accomodations.html')

@app.route('/sdestination')
def sdestination():
    return render_template('destination.html')

@app.route('/destination')
def dest():
    return render_template('postdest.html')

@app.route('/restaurant')
def food():
    return render_template('postfood.html')

@app.route('/accomodations')
def accomodation():
    return render_template('poststay.html')

@app.route('/about/<string:cuisine>')
def about(cuisine):
    post = db.engine.execute(f"SELECT * FROM `food` WHERE `cuisine`='{cuisine}'")
    return render_template('about.html', post=post)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup')
def user_signup():
    return render_template('signup.html')
    
@app.route('/login')
def user_login():
    return render_template('login.html')

@app.route('/delete')
def deletepage():
    return render_template('deleteacct.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

#--------------------------------------------------------------------------------------
#           DB QUERY ROUTES
#--------------------------------------------------------------------------------------

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method=="POST":
        uname=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        city=request.form.get('city')
        password=request.form.get('password')
        
        #print(uname,email,phone,city)
        encpassword=generate_password_hash(password)
        user=User.query.filter_by(uname=uname).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or username is already taken","warning")
            return render_template("signup.html")
        new_user=db.engine.execute(f"INSERT INTO `user` (`uname`,`email`,`password`,`phone`, `city` ) VALUES ('{uname}','{email}','{encpassword}','{phone}','{city}')")
        flash("Signed in successfully!","success")
        return render_template('signup.html')
        
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    posts = User.query.all()
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("login Succesful", "success")
            return render_template('index.html')
        else:
            flash("Invalid credentials", "danger")
            return render_template("login.html")
    return render_template('index.html', posts=posts)

@app.route("/sfood#", methods=['POST', 'GET'])
def test2():
    return "happy"

@app.route('/destination', methods=['POST', 'GET'])
def post_dest():
    post=Destination.query.all()
    if(request.method=="POST"):
        cat=request.form.get('cat')
        name=request.form.get('loc')
        blog=request.form.get('blog')
        country=request.form.get('count')
        destination=Destination.query.filter_by(name=name).first()
        new_dest=db.engine.execute(f"INSERT INTO `destination` (`category`,`name`,`blog`,`country`) VALUES ('{cat}','{name}','{blog}','{country}')")
        flash("Posted","primary")
        return redirect('/destination')
    
    return render_template("index.html", post=post)

@app.route('/food', methods=['POST', 'GET'])
def post_food():
    if(request.method=='POST'):
        resname=request.form.get('resname')
        locname=request.form.get('loc')
        cuisine=request.form.get('cuisine')
        blog=request.form.get('blog')
        new_food=db.engine.execute(f"INSERT INTO `food` (`resname`,`locname`,`cuisine`,`blog`) VALUES ('{resname}','{locname}','{cuisine}','{blog}')")
        flash("posted", "primary")
        return redirect('/restaurant')

    return render_template("postfood.html")

@app.route('/stay', methods=['POST', 'GET'])
def post_stay():
    if(request.method=='POST'):
        name=request.form.get('name')
        locname=request.form.get('locname')
        budget=request.form.get('budget')
        blog=request.form.get('blog')
        review=request.form.get('rev')
        new_stay=db.engine.execute(f"INSERT INTO `accomodation` (`name`,`locname`,`budget`,`review`,`blog`) VALUES ('{name}','{locname}','{budget}','{review}','{blog}')")
        flash("posted", "primary")
        return redirect('/stay')

    return render_template("poststay.html")

@app.route('/foodresult/<string:cuisine>')
def foodresult(cuisine):
    post = db.engine.execute(f"SELECT * FROM `food` WHERE `cuisine`='{cuisine}'")
    return render_template('foodresult.html', post=post)

@app.route('/accomodation', methods=['POST','GET'])
def accomresultbudget():
    minbudget=request.form.get('minbudget')
    maxbudget=request.form.get('maxbudget')
    rev = request.form.get('review')
    if(maxbudget and minbudget and rev):
        value=db.engine.execute(f"SELECT * from `accomodation` WHERE `budget`>'{minbudget}' AND `budget`<'{maxbudget}' AND `review`>'{rev}' ORDER BY `review` ASC ")
    elif(maxbudget and minbudget):
        value=db.engine.execute(f"SELECT * from `accomodation` WHERE `budget`>'{minbudget}' AND `budget`<'{maxbudget}' ORDER BY `budget` ASC ")
    elif(rev):
        value=db.engine.execute(f"SELECT * from `accomodation` WHERE `review`>'{rev}' ORDER BY `review` ASC ")

    return render_template('accomresult.html', value=value)

@app.route('/stayresult/<string:loc>')
def accomresultloc(loc):
    value=db.engine.execute(f"SELECT * from `accomodation` WHERE `locname`='{loc}' ORDER BY `review` ASC")
    return render_template('accomresult.html', value=value)

@app.route('/sightresult/<string:cat>')
def sightsresult(cat):
    value=db.engine.execute(f"SELECT * from `destination` WHERE `category`='{cat}' ")
    
    return render_template("sightresult.html", value=value)

@app.route('/delete' , methods=['POST', 'GET'])
def deleteacct():
    user=current_user.uname
    id=current_user.id
    entuser=request.form.get('name')
    password=request.form.get('password')
    if(user==entuser and check_password_hash(current_user.password,password)):
        new_del=db.engine.execute(f"DELETE from `user` WHERE `id`='{id}' ")
        flash('Account deleted', 'success')
    else:
        flash("Invalid credentials", "danger")
        return render_template("deleteacct.html")
        
    return render_template('deleteacct.html')



app.run(debug=True)

