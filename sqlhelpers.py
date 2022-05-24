from app import mysql, session
from blockchain import Block, Blockchain
from datetime import date
from datetime import datetime
#custom exceptions for transaction errors
class InvalidTransactionException(Exception): pass
class InsufficientFundsException(Exception): pass
# o clasa tabel care reprezinta tabelul din baza de date mysql
class Table():
#constructor
    def __init__(self, table_name, *args): 
        self.table = table_name
        self.columns = "(%s)" %",".join(args)
        self.columnsList = args

#verificare tabel nou, la succes , creeare tael
        if isnewtable(table_name):
            create_data = ""
            for column in self.columnsList:
                create_data += "%s varchar(100)," %column

            cur = mysql.connection.cursor() #create the table
            cur.execute("CREATE TABLE %s(%s)" %(self.table, create_data[:len(create_data)-1]))
            cur.close()

    #functie care preia toate valorile din tabel
     # in python pentru a scrie si executa queries avem nevoie de un cursor
    def getall(self):
        cur = mysql.connection.cursor() # definirea asa zisului cursor
        result = cur.execute("SELECT * FROM %s" %self.table) 
        data = cur.fetchall(); return data # in data salvam valorile returnate de query

    # aici am definit fucntia care ne intoarce numarul de fonduri ale unui utilizator
    def returnBalance(self,utilizator):
        cur = mysql.connection.cursor() #cursor
        sold = 0 # variabila in care vom intoarce fondurile
        #pentru a calcula suma de bani(stirpe) a utilizatorului, vom avea nevoie de 2 valori
        # I suma de bani primita a utilizatorului. pe aceasta o vom obtine , adunand suma valorilor din tranzactii , unde numele utilizatorului concide cu numele recipientului din tranzactie
        suma_primita = cur.execute("SELECT SUM(sold_tranzactie) FROM %s WHERE receptor_nume =  \"%s\"" %(self.table,utilizator))
        # daca ce am obtinut la punctul I este mai mare ca 0 , adica desigur daca utilizatorul a primit vreodata bani, atunci soldul va devevni sold + suma_primita
        
        if suma_primita > 0:
            data = cur.fetchone()
            if (data.get('SUM(sold_tranzactie)') is not None):
                sold =data.get('SUM(sold_tranzactie)')
                
         #II suma de bani pe care utilizatorul a trimis-o , deci din perspectiva soldului ceea ce a pierdut. Aceasta suma este obtinuta adunand suma valorilor din pranzactii ca la pucntul anterior , dar in cazul acesta unde numele utilizatorului coincide cu numele senderului din tranzactie.
        suma_trimisa = cur.execute("SELECT SUM(sold_tranzactie) FROM %s WHERE expeditor_nume =  \"%s\"" %(self.table,utilizator))
        # daca utilizatorul a si trimis ceva , deci daca suma este > 0 , atunci soldul devine soldul vechi - suma_trimisa
        if suma_trimisa > 0:
             data = cur.fetchone()

             if (data.get('SUM(sold_tranzactie)') is not None):
                 sold = sold - (data.get('SUM(sold_tranzactie)'))

        return sold  # intoarcem valoarea finala , care reprezinta fondurile de care dispune utilizatorul in prezent
    
    #obtinem o valoare din tabel in functie de datele unei coloane

    def getone(self, search, value):
        data = {}; cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %(self.table, search, value)) # intoarce-mi datele din... dupa criteriul (unde conditie ...)
        
        if result > 0: data = cur.fetchone() # daca exista astfel de valori intoarce-mi 1.Diferenta e ca aici in loc de fetch all folosim fetch one
            
        cur.close(); return data


    #stergerea unei valori din tabel in functie de val unei coloane
    def deleteone(self, search, value):
        cur = mysql.connection.cursor() #cursor
        cur.execute("DELETE from %s where %s = \"%s\"" %(self.table, search, value)) # sterge din , unde conditie
        mysql.connection.commit(); cur.close() # facem un commit pt a ne asigura ca s-au efectuat schimbarile , inchidem cursorul

    #stergerea tuturor datelor din tabel
    def deleteall(self):
        self.drop() 
        self.__init__(self.table, *self.columnsList)

    #stergerea tabelului din baza de date mqsql. dupa cum am vazut si pana acum se face cu ajutorul unui cursor, unde folosim clasicul drop table , apoi inchidem cursorul
    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" %self.table)
        cur.close()

    #fucntia de introducere valori in tabel
    def insert(self, *args):
        data = ""
        for arg in args: #conversia datelor intr-un format string tip mysql
            data += "\"%s\"," %(arg)

        cur = mysql.connection.cursor() #cursor
        cur.execute("INSERT INTO %s%s VALUES(%s)" %(self.table, self.columns, data[:len(data)-1])) # query de insert
        mysql.connection.commit() # efectuam schimbarile 
        cur.close() # oprire cursor

#executare cod mysql din python
def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

#verifica daca tabelul deja exista 
def isnewtable(tableName):
    cur = mysql.connection.cursor()

    try: #incercam sa obtinem niste valori din tabel
        result = cur.execute("SELECT * from %s" %tableName)
        cur.close()
    except:
        return True # daca nu sunt date in result atunci e un tabel nou
    else:
        return False # daca nu , atunci tabelul deja  exista

#fucntia care verifica daca deja exista userul
def isnewuser(username):
    #accesam tabelul utilizatori si luam toate numele de utilizator di acesta
    users = Table("utilizator", "nume", "email", "nume_utilizator","parola")
    data = users.getall()
    usernames = [user.get('nume_utilizator') for user in data]

    return False if username in usernames else True # daca numele trimis ca parametru se regaseste in lista de nume obtinuta mai sus, acesta deja exista , daca nu , atunci e nou

#functia de trimitere criptomoneda Stirpe de la un user la altul
def send_money(sender, recipient, amount):
    #verificam daca suma trimisa este de tip integer sau float
    try: amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction.") # daca nu, nu putem efectua tranzactia, si trimitem un mesaj de eroare

    #verificam daca un user are suficiente fonduri sa poata face tranzactia , cu exceptia in care senderul este banca.

    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient Funds.") # daca nu trimitem un mesaj de eroare : "fonduri insuficiente"

    #verificam daca userul nu isi trimite banii sie insusi sau daca suma trimisa nu este 0 sau negativa
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException("Invalid Transaction.")

    #verificam daca recipientul destinat tranzactiei exista
    elif isnewuser(recipient):
        raise InvalidTransactionException("User Does Not Exist.")

    #actualizarea in block chain si respectiv mai sql
    blockchain = get_blockchain()
    number = len(blockchain.chain) + 1
    tranzactie = Table("tranzactie","id_tranzactie","expeditor_nume","receptor_nume","data_tranzactie","sold_tranzactie");
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = date.today()
    data_tranz = str(today) +" "+str(current_time)
    tranzactie.insert(number,sender,recipient,data_tranz,amount);
    #Aici trebuie sa creez tabelu pentru tranzactie si sa schimb data cu id_tranzactiei


    #data = "%s-->%s-->%s" %(sender, recipient, amount)
    blockchain.mineaza(Block(number, tranzactie=number))
    sync_blockchain(blockchain)

# Umblam prin tabelul de tranzactii si calculam balanceul
def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()
    tranzactie = Table("tranzactie", "id_tranzactie", "expeditor_nume", "receptor_nume", "data_tranzactie",
                       "sold_tranzactie");

    balance = tranzactie.returnBalance(username)


    return balance
    #loop through the blockchain and update balance
    # for block in blockchain.chain:
    #     data = block.data.split("-->")
    #     if username == data[0]:
    #         balance -= float(data[2])
    #     elif username == data[1]:
    #         balance += float(data[2])
    # return balance

#luam blockchainul din mysql si il convertim la un obiect de tip blockchain
def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", "id", "hash", "antecedent", "id_tranazactie", "nr_cript")
    for b in blockchain_sql.getall():

        blockchain.adaugare(Block(int(b.get('id')),b.get('id_tranazactie'),b.get('antecedent'),  int(b.get('nr_cript'))))

    return blockchain
# obinerea tranzacctiilor 
def get_tranzactii():
    list_trnz = []
    tranzactie = Table("tranzactie", "id_tranzactie", "expeditor_nume", "receptor_nume", "data_tranzactie",
                       "sold_tranzactie");
    for t in tranzactie.getall():
        list_trnz.append(t)
    return list_trnz
    #print(list_trnz)
   # fucntie ot testarea blockchainului
def test_blockchain():
    blockchain_sql = Table("blockchain", "id", "hash", "antecedent", "id_tranazactie", "nr_cript")
    blockchain_sql.deleteall()


#actualizare blokchain in tabelul mysql
def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "id", "hash", "antecedent", "id_tranazactie", "nr_cript")
    blockchain_sql.deleteall()

    for block in blockchain.chain:
        blockchain_sql.insert(str(block.id), block.hash(), block.hashAnterior, block.tranzactie, block.numarCriptare)

