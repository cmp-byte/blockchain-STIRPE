from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from sqlhelpers import *
from forms import *
from functools import wraps
import  time
app = Flask(__name__)

#conexiunea cu baza de date

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0555'
app.config['MYSQL_DB'] = 'stirpedb_v2'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# verific stadiu logare
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return  f(*args, **kwargs)
        else:
            flash("Unauthorized, please login","danger")
            return redirect(url_for('login'))
    return wrap


def log_in_user(username):
    users = Table("utilizator", "nume", "email", "nume_utilizator","parola")
    user = users.getone("nume_utilizator", username)
    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('nume')
    session['email'] = user.get('email')


@app.route("/register", methods=['GET', 'POST'])

# functia de register cu verificarea validitatii datelor introduse
def register():
    form = RegisterForm(request.form)
    users = Table("utilizator", "nume", "email", "nume_utilizator","parola")

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        name = form.name.data

        if isnewuser(username):  # Verificam daca utilizatorul nu exista
            password = sha256_crypt.encrypt(form.password.data) # criptarea parolei
            users.insert(name, email, username, password) # introducerea userului in baza de date
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger') #daca nu este un utilizator nou , trimitem un mesaj cum ca utilizatorul deja exista
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])

# functie de logare utilizator prin nume utilizator si parola 
# se preiau datele introduse , daca nu se gaseste o parola atribuita numelui de utilizator introdus(accpass is none)  => username neexistent
#daca se recunaoste parola criptata si coincide cu cea introdusa, se logheaza utilizatorul
#daca nu, inseamna ca parola nu este valida
def login():
    if request.method == 'POST':
        username = request.form['username']
        candidate = request.form['password']

        users =Table("utilizator", "nume", "email", "nume_utilizator","parola")
        user = users.getone("nume_utilizator", username)
        accpass = user.get('parola')

        if accpass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate, accpass): 
                log_in_user(username)
                flash("You are now logged in.", "succes")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password", 'danger') 
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/transaction", methods = ['GET','POST'])
@is_logged_in
# functia de trimitere bani(stirpe) altui utilizator. 
def transaction():
    form = SendMoney(request.form)
    balance = get_balance(session.get('username')) # obtinem suma de care dispune utilizatorul curent
    if request.method =='POST':
        try:
            send_money(session.get('username'),form.username.data,form.amount.data) # incercam trimiterea
            flash("Money sent",'success') # pt succes
        except Exception as e: # pt esec
            flash(str(e),'danger')
        return redirect(url_for('transaction'))
    return render_template('transaction.html',balance=balance, form=form, page= 'transcation')

@app.route("/buy", methods = ['GET','POST'])
@is_logged_in

# metoda de cumparare criptomonede stirpe 
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))
    if request.method =='POST':
        try:
            send_money("BANK",session.get('username'),form.amount.data) # se incearca trimiterea catre utilizator
            flash("Purchase successful",'success') # in caz de succes
        except Exception as e: #in caz de esec
            flash(str(e),'danger')
        return redirect(url_for('dashboard'))
    return render_template('buy.html',balance=balance, form=form,page ='buy')

@app.route("/logout")
@is_logged_in
# functia de log out , eliberarea sesiunii + mesaj succes
def logout():
    session.clear()
    flash("Logout success", 'success')
    return redirect(url_for('login'))


@app.route("/dashboard")
@is_logged_in
def dashboard():
    blockchain =get_blockchain().chain
    tranzactie =get_tranzactii()
    currentTime = time.strftime("%I:%M %p")
    balance = get_balance(session.get('username'))

    return render_template('dashboard.html', session=session,balance=balance,tranzactie=tranzactie, currentTime =currentTime, blockchain=blockchain, page='dashboard')


@app.route("/")
# In loc sa returnam continutul html, vom return un fisier html folosindu-ne de functia render template
def index():

    return render_template('index.html')


if __name__ == '__main__':

   app.secret_key = 'sercret123'
   app.run(debug=True)
