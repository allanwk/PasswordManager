#!/usr/bin/python3
#Dependencias para a GUI
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import sys

#Dependencias para gerenciamento das senhas
from cryptography.fernet import Fernet
from pyperclip import copy
import re
from time import sleep
import random
import string

#Dependencias Google Drive API
import os.path
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

"""Padrao para identificar site, senha e usuario no arquivo
data apos descriptografado"""
pattern = r"([a-zA-Z0-9!@#$%&* -]*),([a-zA-Z0-9@\.]*),(\w*)"

#Dicionario para armazenar as informacoes de senhas
info = {}

#Carregamento das variáveis de ambiente (IDs das planilhas do Google Sheets),
#caminho do projeto
load_dotenv()
DATA_FILE_ID = os.environ.get("DATA_FILE_ID")
PROJECT_DIR = os.environ.get("PROJECT_DIR")

#Escopos de autorização da API do Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

class Window(QMainWindow):
    """Classe janela para a GUI. Caso não seja provida a chave de acesso válida,
    a GUI renderiza apenas uma janela vazia, não permitindo operações.
    """
    
    def __init__(self, drive_service, key):
        """Inicialização da janela principal"""
        super(Window, self).__init__()
        self.setGeometry(200,200,435,275)
        self.setWindowTitle("Gerenciador de senhas")
        self.key = key
        if self.key != 0:
            self.drive_service = drive_service
            self.initUI()
            self.updateList()
        else:
            self.setWindowTitle("Chave de acesso inválida!")

    def initUI(self):
        """Inicialização dos elementos da interface gráfica"""
        #Lista
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 256, 192))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemDoubleClicked.connect(self.copy_password)

        #Caixas de texto
        self.passwordTextBox = QtWidgets.QLineEdit(self)
        self.passwordTextBox.setGeometry(QtCore.QRect(300, 100, 113, 20))
        self.passwordTextBox.setObjectName("passwordTextBox")
        self.userTextBox = QtWidgets.QLineEdit(self)
        self.userTextBox.setGeometry(QtCore.QRect(300, 50, 113, 20))
        self.userTextBox.setObjectName("userTextBox")
        self.siteTextBox = QtWidgets.QLineEdit(self)
        self.siteTextBox.setGeometry(QtCore.QRect(300, 150, 113, 20))
        self.siteTextBox.setObjectName("siteTextBox")

        #Labels
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

        #Botões
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

    def updateList(self):
        """Atualizar a visualização da lista de senhas"""
        self.listWidget.clear()
        for dict_key in info:
            item = QListWidgetItem(dict_key)
            self.listWidget.addItem(item)
        
    def updateFile(self):
        """Atualizar o arquivo que armazena as senhas e fazer o backup
        no Google Drive"""
        if self.key != 0:
            with open(PROJECT_DIR + '/data.txt', "w+") as data:
                lines = [str(Fernet(self.key).encrypt(bytes("{},{},{}".format(value[0], value[1], site), 'utf-8'))) + "\n" for site, value in info.items()]
                data.writelines(lines)
            media = MediaFileUpload(PROJECT_DIR + '/data.txt')
            file = self.drive_service.files().update(
                                        media_body=media,
                                        fileId=DATA_FILE_ID,
                                        fields='id').execute()

    def copy_password(self):
        """Copiar a senha selecionada para a área de tranferência"""
        copy(info[self.listWidget.currentItem().text()][0])
        self.showMessageDialog("Senha copiada para a área de transferência.")

    def remove_item(self):
        """Remover senha da lista de senhas salvas"""
        info.pop(self.listWidget.currentItem().text(), None)
        self.updateList()
        self.updateFile()
        self.showMessageDialog("Senha removida com sucesso.")

    def add_item(self):
        """Adicionar nova senha a lista"""
        user = self.userTextBox.text()
        password = self.passwordTextBox.text()
        site = self.siteTextBox.text()
        if site not in info:
            info[site] = (password, user)
            self.updateList()
            self.updateFile()
            self.showMessageDialog("Senha adicionada com sucesso.")
            self.passwordTextBox.setText("")
            self.userTextBox.setText("")
            self.siteTextBox.setText("")
        else:
            self.showMessageDialog("Já existe um registro para esse site.")

    def showMessageDialog(self, message):
        """Método helper para mostrar caixas de diálogo"""
        msg = QtWidgets.QMessageBox()
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec_()

    def generate_password(self):
        """Gerador de senhas fortes (15 caracteres)"""
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


def main():
    """Buscando chave de acesso no token (pen drive)
    Caso não seja encontrada, a chave recebe o valor 0, e o drive_service None, 
    invalidando qualquer operação na GUI.
    """
    try:
        f = open("/media/allan/KINGSTON/text.txt", "r")
        key = f.readline().encode()
        f.close()
    except:
        key = 0
        drive_service = None

    #Informações descriptografadas são salvas no dicionário info
    if key != 0:
        with open(PROJECT_DIR + '/data.txt', "r") as data:
            for line in data:
                dec = Fernet(key).decrypt(bytes(line[2:-1], 'utf-8'))
                res = re.search(pattern, str(dec))
                try:
                    info[res.group(3)] = (res.group(1), res.group(2))
                except:
                    pass
        #Autenticacao utilizando credenciais no arquivo JSON ou arquivo PICKLE
        creds = None
        if os.path.exists(PROJECT_DIR + '/token.pickle'):
            with open(PROJECT_DIR + '/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    PROJECT_DIR + '/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(PROJECT_DIR + '/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        #Autenticação google drive
        drive_service = build('drive', 'v3', credentials=creds)

    #Instanciação da GUI
    app = QApplication(sys.argv)
    win = Window(drive_service, key)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()