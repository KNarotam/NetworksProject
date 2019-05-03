import socket
import sys
import os
import time
from time import sleep
from os import walk
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel, QTextBrowser, QInputDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot


pathName = os.getcwd()
##########################################################
################# Creating the Interface #################
##########################################################

###############################################################
        
class ClientInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Kish and Matt's FTP Client"
        self.left = 150
        self.top = 150
        self.width = 810
        self.height = 720
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color:rgb(106, 106, 106)")

        #### Address Interface Features ####
        # Set Address Label
        self.labelAddress = QLabel('Server Address', self)
        self.labelAddress.setGeometry(10, 10, 125, 16)
        self.labelAddress.setFont(QFont('Copperplate Gothic Bold', 10))
        self.labelAddress.setStyleSheet("color: rgb(255, 255, 0);")
        
        # Create the Address Text box
        self.textboxAddress = QLineEdit(self)
        self.textboxAddress.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.textboxAddress.move(10, 30)
        self.textboxAddress.resize(170, 30)
        
        # Create the button for the Address
        self.buttonAddress = QPushButton('Connect to server', self)
        self.buttonAddress.setToolTip('Press this button to connect to the typed address')
        self.buttonAddress.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.buttonAddress.move(190, 30)
        self.buttonAddress.resize(100, 30)
        self.buttonAddress.clicked.connect(self.connect)

        #### Login Interface Features ####
        # Set Username Label
        self.labelUsername = QLabel('Username', self)
        self.labelUsername.setGeometry(10, 80, 125, 16)
        self.labelUsername.setFont(QFont('Copperplate Gothic Bold', 10))
        self.labelUsername.setStyleSheet("color: rgb(255, 255, 0);")
        
        # Create the Username Text box
        self.textboxUsername = QLineEdit(self)
        self.textboxUsername.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.textboxUsername.move(10, 100)
        self.textboxUsername.resize(170, 30)

        # Set Password Label
        self.labelPassword = QLabel('Password', self)
        self.labelPassword.setGeometry(190, 80, 125, 16)
        self.labelPassword.setFont(QFont('Copperplate Gothic Bold', 10))
        self.labelPassword.setStyleSheet("color: rgb(255, 255, 0);")
        
        # Create the Password Text box
        self.textboxPassword = QLineEdit(self)
        self.textboxPassword.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.textboxPassword.move(190, 100)
        self.textboxPassword.resize(170, 30)
        
        # Create the button for the Login
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.setToolTip('Press this button to login')
        self.buttonLogin.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.buttonLogin.move(370, 100)
        self.buttonLogin.resize(100, 30)
        self.buttonLogin.clicked.connect(self.begin)

        # Create the User Input text box
        self.textboxUserInput = QLineEdit(self)
        self.textboxUserInput.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.textboxUserInput.move(10, 160)
        self.textboxUserInput.resize(200, 30)

        # Create the button for the entering user input
        self.buttonInput = QPushButton('Enter', self)
        self.buttonInput.setToolTip('Press this button to enter your choice')
        self.buttonInput.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.buttonInput.move(220, 160)
        self.buttonInput.resize(80, 30)
        self.buttonInput.clicked.connect(self.enter)

        # Set Menu Label
        self.labelMenu = QLabel('COMMANDS LIST\nPWD: Print Remote and Local Directory\nCWLD: Change Local Directory\nCWRD: Change Remote Directory\nRECV: Receive File\nSEND: Send File', self)
        self.labelMenu.setGeometry(600, 0, 200, 80)
        self.labelMenu.setStyleSheet("color: rgb(255, 0, 255);")

        # Create Display Window
        self.displayBrowser = QTextBrowser(self)
        self.displayBrowser.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.displayBrowser.move(10, 200)
        self.displayBrowser.resize(720, 500)

        # Create the button for the entering user input
        self.buttonExit = QPushButton('EXIT', self)
        self.buttonExit.setToolTip('Press this button to exit the program')
        self.buttonExit.setStyleSheet("background-color:rgb(255, 0, 0)")
        self.buttonExit.move(740, 670)
        self.buttonExit.resize(50, 30)
        self.buttonExit.clicked.connect(self.close)

        self.show()

        self.welcome()
       

##########################################################
################# Functions #################
##########################################################

    @pyqtSlot()
    # Button function for connecting to the server
    def connect(self):
        self.s = socket.socket()
        address = self.textboxAddress.text()
        port = 21

        self.s.connect((address, port))
        self.s.recv(1024)

        self.displayBrowser.append("Connected to: " + address + "\n")
        self.displayBrowser.append("Enter your username and password\n")  

    # Send function: for message and reply messages
    def send(self,message = ''):
        # Using the bytes function, we use the "source" which is the message object returns
        # The message is encoded in UTF-8
        self.s.send(bytes(message + ('\r\n'), 'UTF-8'))

    # Receive function that will return what is received
    def receive(self):
        # Receives data from the socket with "buffsize" of 1024
        recMessage = self.s.recv(1024)
        code = recMessage.decode()
        self.displayBrowser.append(code)
        # Returns the received value as a string
        return (recMessage)

    # Combined function that will send and return the received response from the server
    def combinedSendReceive(self, message = ''):
        self.send(message)
        return self.receive()

    # Function that changes the connection to PASSIVE
    def passive(self):
        while True:
            temp = ''
            message = ('PASV')
            message = self.combinedSendReceive(message)
            # The message was sent using the "send()" function, and needs to be decoded
            message = message.decode()
            # Find the first (
            newMessage = message.split('(')
            # Go to last character in message and find )
            newMessage = newMessage[-1].split(')')
            # Get the new address
            address = newMessage[0].split(',')
            # Add . to create a new IP address
            newIP = '.'.join(address[:4])
            # Use the formula to calculate the port number
            newPort = int(address[4])*256 + int(address[5])
            return (newIP, newPort)
            break

    # Function that will print out the current local directory
    def localDirectory(self, pathName = ''):
        # On every pass of the loop, os.walk gives us:
            # dirName = next directory found
            # subDirList = list of sub-directories in current directory
            # fileList = a list of files in current directory
        for(dirName, subDirList, fileList) in walk(pathName):
            #path = dirName
            self.displayBrowser.append(dirName)
            break
        return (dirName)

    # Function that will browse the current directory and print out all the files and folders
    def  browseDirectory(self, pathName=''):
        for(dirName, subDirList, fileList) in walk(pathName):
            break
        for object in subDirList:
            self.displayBrowser.append("\nFolder: ")
            self.displayBrowser.append(object)
        for object in fileList:
            self.displayBrowser.append("\nFile: ")
            self.displayBrowser.append(object)
        return (dirName, subDirList, fileList)

    # Function that will retrieve/download files
    def retrieveFile(self, fileName = ''):
        # First we need to enter passive mode
        newIP, newPort = self.passive()
        passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        passiveSocket.connect((newIP, newPort))
        self.combinedSendReceive('RETR ' + fileName)
        # using the open function, we will open the file to be uploaded
        # We set the mode to be wb
        # w = open for writing, truncating the file first
        # b = binary mode
        newFile = open(fileName, 'wb')
        message = ''
        temp = 'hi'

        # Uploading the file, while there is data present
        while temp != b'':
            time.sleep(0.1)
            sys.stdout.write("\r" "downloading")
            sys.stdout.flush()
            temp = passiveSocket.recv(4194304)
            newFile.write(temp)

        newFile.close()
        test = self.receive()

    # Function that will send/upload files
    def sendFile(self, fileName = ''):
        # First need to enter passive mode
        newIP, newPort = self.passive()
        passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        passiveSocket.connect((newIP, newPort))
        self.send('STOR ' + fileName)
        pathOfFile = pathName +'/' + fileName
        # using the open function, open the file and return corresponding object
        # We set the mode to rb:
        # r = open for reading (default)
        # b = binary mode
        file = open(pathOfFile, 'rb')
        # Retrieve the size of the file using stat function and specifically the member value of "st_size" which is the size of the files in bites, the 6th member return value
        sizeOfFile = os.stat(pathOfFile)[6]
        # set status of the file: open or closed
        fileStatus = True
        # Initialize the variables for uploading as it will be done in smaller pieces 
        position = 0
        # buffer size to 4 MB
        bufferSize = 4194304
        packets = sizeOfFile/bufferSize
        timeout = 100/packets
        counter = 0

        # Transferring the file
        while fileStatus:
            counter = counter + timeout

            if counter > 100:
                counter = 100
            
            # Wait for 100 milliseconds
            time.sleep(.1)
            sys.stdout.write("\r%d%%" %counter)
            sys.stdout.flush()
            file.seek(position)
            position += bufferSize

            if position >= sizeOfFile:
                partial = file.read(-1)
                fileStatus = False
            else:
                partial = file.read(bufferSize)
            passiveSocket.send(partial)

            file.seek(position)
        file.close()
        self.receive()

    # Function to list the directory
    def listDirectory(self):
        # First we need to enter passive mode
        newIP, newPort = self.passive()
        passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        passiveSocket.connect((newIP, newPort))
        self.combinedSendReceive('LIST')
        # create an empty array that will store the directory
        directory = []

        # wait 1 second before receiving the directory and printing it out
        time.sleep(.1)
        contentOfDirectory = passiveSocket.recv(1024)
        # decode the contents of the directory
        contentOfDirectory = contentOfDirectory.decode()
        #print(contentOfDirectory)
        # add the contents of the directory to the directory array
        directory = contentOfDirectory.split('\n')
        directory = directory[:-1]

        # create two arrays one for the folders and one for the files
        foldersInDirectory = []
        filesInDirectory = []

        # Go through every object (folder and file) in directory and add it to the respective array
        for object in directory:
            if object[0] == 'd':
                foldersInDirectory.append(object)
                self.displayBrowser.append("Folder:")
                self.displayBrowser.append(object)
            else:
                filesInDirectory.append(object)
                self.displayBrowser.append("File: ")
                self.displayBrowser.append(object)

        # Categorize all the folders in the directory
        for counter, tempFolder in enumerate(foldersInDirectory):
            contentOfDirectory = tempFolder.split(':')
            tempFolder = contentOfDirectory[0]
            tempFolder = tempFolder[3:]
            foldersInDirectory[counter] = tempFolder

        # Categorize all the files in the directory
        for counter, tempFile in enumerate(filesInDirectory):
            contentOfDirectory = tempFile.split(':')
            tempFile = contentOfDirectory[0]
            tempFile = tempFile[3:]
            filesInDirectory[counter] = tempFile

        message = ('ABOR')
        passiveSocket.send(bytes(message + ("\r\n"), "UTF-8"))
        self.receive()
        passiveSocket.close()
        return (foldersInDirectory, filesInDirectory)

    # Function to show welcome message
    def welcome(self):
        self.displayBrowser.append("Welcome to the FTP Client.\nStep 1: Type in the server address.\nStep 2: Enter login information")

    # Button function for beggininng the program after logging in
    def begin(self):
        userName = self.textboxUsername.text()
        #userName = 'anonymous'
        self.combinedSendReceive('USER ' + userName)
        password = self.textboxPassword.text()
        #password = 'anonymous@'
        self.combinedSendReceive('PASS ' + password)

    # Button function for entering the user input
    def enter(self):
        userInput = self.textboxUserInput.text()
        self.displayBrowser.append(userInput)
        global pathName
        #while True:
        if userInput == 'PWD':
            directory = ''
            self.displayBrowser.append('Remote Directory')
            message = 'PWD'
            self.send(message)
            directory = self.s.recv(1024)
            directory = directory.decode()
            code = directory.split('i')
            code = code[0].split(' ')
            code = code[0]

            if code == '257':
                directory = directory.split('"')
                directory = directory[1]
                self.displayBrowser.append('"' + directory + '"')
            else:
                self.displayBrowser.append('"' + directory + '"')
            
            self.listDirectory()
            self.displayBrowser.append('\nLocal Directory')

            self.localDirectory(pathName)
            self.browseDirectory(pathName)
            return (directory)
            
##############################################
        if userInput == 'CWLD':
            option, okPressed = QInputDialog.getText(self, "Your option", "Choose Directory (Press home to go to home directory)", QLineEdit.Normal, "")
            if option == "home":
                pathName = 'C:\\Users\\knaro\\Documents\\GitHub\\NetworksProject'
            else:
                pathName = pathName + '\\' + option

            self.localDirectory(pathName)
            self.browseDirectory(pathName)
            return (pathName)
        
##############################################
        if userInput == 'CWRD':
            option, okPressed = QInputDialog.getText(self, "Your option", "Choose Directory (Press up to go up a directory)", QLineEdit.Normal, "")
            if option == "up":
                self.combinedSendReceive('CDUP')
            else:
                self.combinedSendReceive('CWD ' + option)

##############################################
        if userInput == "RECV":
            option, okPressed = QInputDialog.getText(self, "Your option", "What type of file are you RECEIVING? (ASCII or Image)", QLineEdit.Normal, "")
            if option == "ASCII":
                os.path = pathName
                message = "TYPE A"
                self.send(message)
                downloadFile, okPressed = QInputDialog.getText(self, "Your option", "What is the name of the file?", QLineEdit.Normal, "")
                
                while True:
                    code = self.receive()
                    code = code.decode()
                    code = code.split("'")
                    code = code[0].split(' ')
                    code = code[0]

                    if code == '226':
                        message = "ABOR"
                        self.combinedSendReceive(message)
                        self.receive()
                        break
                    else:
                        break

                self.retrieveFile(downloadFile)

            if option == "Image":
                os.path = pathName
                message = "TYPE I"
                self.send(message)
                downloadFile, okPressed = QInputDialog.getText(self, "Your option", "What is the name of the file?", QLineEdit.Normal, "")
                
                while True:
                    code = self.receive()
                    code = code.decode()
                    code = code.split("'")
                    code = code[0].split(' ')
                    code = code[0]

                    if code == '226':
                        message = "ABOR"
                        self.combinedSendReceive(message)
                        self.receive()
                        break
                    else:
                        break

                self.retrieveFile(downloadFile)

##############################################
        if userInput == "SEND":
            option, okPressed = QInputDialog.getText(self, "Your option", "What type of file are you SENDING? (ASCII or Image)", QLineEdit.Normal, "")
            if option == "ASCII":
                os.path = pathName
                message = "TYPE A"
                self.send(message)
                uploadFile, okPressed = QInputDialog.getText(self, "Your option", "What is the name of the file?", QLineEdit.Normal, "")

                while True:
                    code = self.receive()
                    code = code.decode()
                    code = code.split("'")
                    code = code[0].split(' ')
                    code = code[0]

                    if code == '226':
                        message = "ABOR"
                        self.combinedSendReceive(message)
                        self.receive()
                        break
                    else:
                        break

                self.sendFile(uploadFile)

            if option == "Image":
                os.path = pathName
                message = "TYPE I"
                self.send(message)
                uploadFile, okPressed = QInputDialog.getText(self, "Your option", "What is the name of the file?", QLineEdit.Normal, "")

                while True:
                    code = self.receive()
                    code = code.decode()
                    code = code.split("'")
                    code = code[0].split(' ')
                    code = code[0]

                    if code == '226':
                        message = "ABOR"
                        self.combinedSendReceive(message)
                        self.receive()
                        break
                    else:
                        break

                self.sendFile(uploadFile)


        self.textboxUserInput.setText("")
   


###################################################################
       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ci = ClientInterface()
    pathName = 'C:\\Users\\knaro\\Documents\\GitHub\\NetworksProject'
    sys.exit(app.exec_())