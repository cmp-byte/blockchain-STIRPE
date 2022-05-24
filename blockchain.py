import sys
from hashlib import sha256



def hasing(*args):
    hasing_text = ""; h = sha256()
    for i in args:
        hasing_text += str(i)
    h.update(hasing_text.encode('utf-8'))
    return  h.hexdigest()


class Block():

    def __init__(self,id = 0, tranzactie =0, hashAnterior="0"*64, numarCriptare = 0):
        self.id = id
        self.hashAnterior = hashAnterior
        self.tranzactie = tranzactie
        self.numarCriptare = numarCriptare
    def hash(self):
       return hasing(self.hashAnterior, self.id, self.tranzactie, self.numarCriptare)

    def __str__(self):
        return str(" Block id: %s "
                   "\n Hash: %s "
                   "\n hashAnterior: %s "
                   "\n Tranzactie: %s "
                   "\n numarCriptare: %s "
                   "\n"
                   %(self.id,self.hash(),self.hashAnterior,self.tranzactie,self.numarCriptare))

class Blockchain():
    grad_securitate = 4

    def __init__(self):
        self.chain =[]

    def adaugare(self,block):
        self.chain.append(block)

    def stergere (self,block):
        self.chain.remove((block))

    def mineaza(self,block):
        try:
            block.hashAnterior = self.chain[-1].hash()
        except IndexError:
            pass
        while True:
            if block.hash()[:self.grad_securitate] == "0"* self.grad_securitate:
                self.adaugare(block)
                break
            else:
                block.numarCriptare +=1

    def valid(self):
        for i in range(1,len(self.chain)):
            _previous = self.chain[i].hashAnterior
            _current = self.chain[i-1].hash()
            if _previous != _current or _current[:self.grad_securitate] != "0"* self.grad_securitate:
                return False
        return True

def main():
   list = [1,2,'6',"4"]
   chain = Blockchain()
   num = 0
   for data in list:
       num += 1
       chain.mineaza(Block(num,data))
   print(len(chain.chain))
   for block in chain.chain:
       print(block)

   #chain.chain[2].data = "New DATa";
   #chain.mine(chain.chain[2])
   print(chain.valid())
if __name__ == '__main__':
    main()