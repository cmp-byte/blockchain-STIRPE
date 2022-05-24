from wtforms import Form, StringField, DecimalField, IntegerField, TextAreaField, PasswordField, validators

# aici am definit clasele ce ne ajuta la functiile din app.py
# un formular de inregistrare ce contine nume , nume utilizator , email si parola , respectiv verif parola
class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=50)]) #nume intre  1 si 50 caract
    username = StringField('Username', [validators.Length(min=4, max=25)]) # nume utilizator intre 4 si 25 caract
    email = StringField('Email', [validators.Length(min=6, max=50)]) # email intre 6 si 50 carcat
    password = PasswordField('Password', [validators.DataRequired(),
                                   validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

    # formular tranzactie ( trimitere bani ) 
class SendMoney(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)]) # nume intre 4 si 25 caract 
    amount = StringField('Amount',[validators.Length(min=1, max=50)]) # suma trimisa minim 1 unitate(desi paote fi introdus 0 acest caz este tratat in fucntia de trimitere bani)  maxim fff multe

    # formular cumaprare 
class BuyForm(Form):
    amount = StringField('Amount', [validators.Length(min=1, max=50)]) # formular de cumaparare stirpe (by default senderul este banca), la fel ca si mai sus intre 1 si 10^50 unitati, cazurile unde val sunt <=0 fiind tratate in fct de cumparare