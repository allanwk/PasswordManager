from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import sys
from cryptography.fernet import Fernet
from pyperclip import copy
import re
from time import sleep
import random
import string

pattern = r"([a-zA-Z0-9!@#$%&* -]*),([a-zA-Z0-9@\.]*),(\w*)"
info = {}
key = ""

class Window(QMainWindow):
    """Classe janela para a GUI. Caso não seja provida a chave de acesso válida,
    a GUI renderiza apenas uma janela vazia, não permitindo operações.
    """
    
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200,200,435,275)
        self.setWindowTitle("Gerenciador de senhas")
        if key != 0:
            self.initUI()
            self.updateList()
        else:
            self.setWindowTitle("Chave de acesso inválida!")

    #Método para criar os elementos da interface gráfica
    def initUI(self):
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 256, 192))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemDoubleClicked.connect(self.copy_password)
        self.passwordTextBox = QtWidgets.QLineEdit(self)
        self.passwordTextBox.setGeometry(QtCore.QRect(300, 100, 113, 20))
        self.passwordTextBox.setObjectName("passwordTextBox")
        self.userTextBox = QtWidgets.QLineEdit(self)
        self.userTextBox.setGeometry(QtCore.QRect(300, 50, 113, 20))
        self.userTextBox.setObjectName("userTextBox")
        self.siteTextBox = QtWidgets.QLineEdit(self)
        self.siteTextBox.setGeometry(QtCore.QRect(300, 150, 113, 20))
        self.siteTextBox.setObjectName("siteTextBox")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(300, 30, 47, 13))
        self.label.setObjectName("label")
        self.label.setText("Usuário")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(300, 80, 47, 13))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Senha")
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(300, 130, 47, 13))
        self.label_3.setObjectName("label_3")
        self.label_3.setText("Site")
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 251, 16))
        self.label_4.setObjectName("label_4")
        self.label_4.setText("Senhas Disponíveis - Clique duplo")
        self.label_5 = QtWidgets.QLabel(self)
        self.label_5.setGeometry(QtCore.QRect(300, 10, 115, 16))
        self.label_5.setObjectName("label_5")
        self.label_5.setText("Registrar senhas")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(300, 210, 111, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Adicionar")
        self.pushButton.clicked.connect(self.add_item)
        self.pushButtonDelete = QtWidgets.QPushButton(self)
        self.pushButtonDelete.setGeometry(QtCore.QRect(10, 230, 135, 23))
        self.pushButtonDelete.setText("Remover item selecionado")
        self.pushButtonDelete.clicked.connect(self.remove_item)
        self.pushButtonGenerate = QtWidgets.QPushButton(self)
        self.pushButtonGenerate.setGeometry(QtCore.QRect(300, 180, 111, 23))
        self.pushButtonGenerate.setText("Gerar senha forte")
        self.pushButtonGenerate.clicked.connect(self.generate_password)

    #Atualizar a visualização da lista de senhas
    def updateList(self):
        self.listWidget.clear()
        for key in info:
            item = QListWidgetItem(key)
            self.listWidget.addItem(item)
        
    #Atualizar o arquivo que armazena as senhas
    def updateFile(self):
        if key != 0:
            with open("data.txt", "w+") as data:
                lines = [str(Fernet(key).encrypt(bytes("{},{},{}".format(value[0], value[1], site), 'utf-8'))) + "\n" for site, value in info.items()]
                data.writelines(lines)

    #Copiar a senha selecionada para a área de tranferência
    def copy_password(self):
        copy(info[self.listWidget.currentItem().text()][0])
        self.showMessageDialog("Senha copiada para a área de transferência.")

    #Remover senha da lista de senhas salvas
    def remove_item(self):
        info.pop(self.listWidget.currentItem().text(), None)
        self.updateList()
        self.updateFile()
        self.showMessageDialog("Senha removida com sucesso.")

    #Adicionar nova senha a lista
    def add_item(self):
        user = self.userTextBox.text()
        password = self.passwordTextBox.text()
        site = self.siteTextBox.text()
        if site not in info:
            info[site] = (password, user)
            self.updateList()
            self.updateFile()
            self.showMessageDialog("Senha adicionada com sucesso.")
        else:
            self.showMessageDialog("Já existe um registro para esse site.")

    #Método helper para mostrar caixas de diálogo
    def showMessageDialog(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec_()

    #Gerador de senhas fortes (15 caracteres)
    def generate_password(self):
        symbols = '!@#$%&*'
        generate_pass = ''.join([random.choice(  
                        string.ascii_letters + string.digits + symbols)  
                        for n in range(15)])  
 
        hasNumber = False
        hasUpper = False
        hasLower = False
        hasSymbol = False
    
        for letter in generate_pass:
            if letter in string.digits:
                hasNumber = True
            if letter in string.ascii_lowercase:
                hasLower = True
            if letter in string.ascii_uppercase:
                hasUpper = True
            if letter in symbols:
                hasSymbol = True              
        if hasNumber and hasUpper and hasLower and hasSymbol:
            self.passwordTextBox.setText(generate_pass)
        else:
            self.generate_password()

"""Buscando chave de acesso no token (pen drive)
Caso não seja encontrada, a chave recebe o valor 0, invalidando qualquer
operação na GUI.
"""
try:
    f = open("F:/text.txt", "r")
    key = f.readline().encode()
    f.close()
except:
    key = 0

#Informações descriptografadas são salvas no dicionário info
def main():
    if key != 0:
        with open("data.txt", "r") as data:
            for line in data:
                dec = Fernet(key).decrypt(bytes(line[2:-1], 'utf-8'))
                res = re.search(pattern, str(dec))
                try:
                    info[res.group(3)] = (res.group(1), res.group(2))
                except:
                    pass

    #Instanciação da GUI
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()