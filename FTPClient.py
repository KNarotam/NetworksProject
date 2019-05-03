# Authored by Kishan Narotam (717 931)

import socket
import sys
import os
import time
from time import sleep
from os import walk

# Creating the socket for the client
s = socket.socket()

# Send function: for message and reply messages
def send(message = ''):
    # Using the bytes function, we use the "source" which is the message object returns
    # The message is encoded in UTF-8
    s.send(bytes(message + ('\r\n'), 'UTF-8'))

# Receive function that will return what is received
def receive():
    # Receives data from the socket with "buffsize" of 1024
    recMessage = s.recv(1024)
    # Returns the received value as a string
    return (recMessage)

# Combined function that will send and return the received response from the server
def combinedSendReceive(message = ''):
    send(message)
    return receive()

# Function that will print out the current directory
def localDirectory(pathName = ''):
    # On every pass of the loop, os.walk gives us:
        # dirName = next directory found
        # subDirList = list of sub-directories in current directory
        # fileList = a list of files in current directory
    for(dirName, subDirList, fileList) in walk(pathName):
        print("You are in directory:\n",dirName)
        break

# Function that will browse the current directory
def  browseDirectory(pathName=''):
    for(dirName, subDirList, fileList) in walk(pathName):
        print(subDirList,'\n',fileList,'\n')
        break

# Function that changes the connection to PASSIVE
def passive():
    while True:
        temp = ''
        message = ('PASV')
        send(message)
        message = (s.recv(1024))
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

# Function that will send/upload files
def sendFile(fileName = ''):
    # First need to enter passive mode
    newIP, newPort = passive()
    passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    passiveSocket.connect((newIP, newPort))
    send('STOR ' + fileName)
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
    receive()

# Function that will retrieve/download files
def retrieveFile(fileName = ''):
    # First we need to enter passive mode
    newIP, newPort = passive()
    passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    passiveSocket.connect((newIP, newPort))
    combinedSendReceive('RETR ' + fileName)
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
        sys.stdout.write("\r" "hold")
        sys.stdout.flush()
        temp = passiveSocket.recv(4194304)
        newFile.write(temp)

    newFile.close()

# Function to list the directory
def listDirectory():
    # First we need to enter passive mode
    newIP, newPort = passive()
    passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    passiveSocket.connect((newIP, newPort))
    combinedSendReceive('LIST')
    # create an empty array that will store the directory
    directory = []

    # wait 1 second before receiving the directory and printing it out
    time.sleep(.1)
    contentOfDirectory = passiveSocket.recv(1024)
    # decode the conetents of the directory
    contentOfDirectory = contentOfDirectory.decode()
    print(contentOfDirectory)
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
        else:
            filesInDirectory.append(object)

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

    print(foldersInDirectory)
    print(filesInDirectory)

    message = ('ABOR')
    passiveSocket.send(bytes(message + ("\r\n"), "UTF-8"))
    receive()

###############################################

# Executing the program
#address = input("Enter the address of the server: ")
#address = "demo.wftpserver.com"
#address = "test.rebex.net"
address = '10.0.0.24'
port = 21

s.connect((address, port))
s.recv(1024)

os.system('cls' if os.name == 'nt' else 'clear')
userName = input("Enter the user name: ")
#userName = 'anonymous'
combinedSendReceive('USER ' + userName)
password = input("Enter the password: ")
#password = 'anonymous@'
combinedSendReceive('PASS ' + password)

# Get current working directory
pathName = os.getcwd()
buff = 1024

while True:
    # clear the command window
    os.system('cls' if os.name == 'nt' else 'clear')
    print("1: Print Remote and Local Directory")
    print("2: Change Directory")
    print("3: Receive File")
    print("4: Send File")
    print("EXIT: Exit")

    userInput = input("Choose an option: ")

############ Print Local Directory ############
    if userInput == '1':
        while True:
            directory = ''
            print('Remote Directory')
            message = 'PWD'
            send(message)
            directory = s.recv(1024)
            directory = directory.decode()
            temp = directory.split('i')
            temp = temp[0].split(' ')
            temp = temp[0]

            if temp == '257':
                directory = directory.split('"')
                directory = directory[1]
                print('"' + directory + '"')
            else:
                print('"' + directory + '"')
            
            listDirectory()
            print('\nLocal Directory')
            localDirectory(pathName)
            browseDirectory(pathName)
            print(input('Hit Enter'))
            break

############ Change Directory ############
    if userInput == '2':
        while True:
            print('1: Change local directory')
            print('2: Change remote directory')
            print('3: Go to main menu')

            userInputSub = input("Which directory: ")

            if userInputSub == "1":
                print("Change LOCAL directory")
                print("Type "'home'" to go to home directory or name of folder")
                newPathName = input("Input: ")

                if newPathName == "home":
                    pathName = 'C:\\Users\\knaro\\Documents\\GitHub\\NetworksProject'
                else:
                    pathName = pathName + '\\' + newPathName

                localDirectory(pathName)
                browseDirectory(pathName)
                print(input("Press Enter"))

            if userInputSub == "2":
                print("Change REMOTE directory")
                print("Choose to go up one level or into one of the folders")
                option = input("Input: ")

                if option == "up":
                    combinedSendReceive('CDUP')
                else:
                    combinedSendReceive("CWD " + option)

                listDirectory()
                print(input("Press Enter"))

            if userInputSub == "3":
                break

############ Receive File ############

    if userInput == '3':
        while True:
            print("What type of file are you RECEIVING?")
            print("1: ASCII")
            print("2: Image")
            print('3: Go to main menu')
            userInputSub = input("Which type of file: ")

            if userInputSub == "1":
                os.path = pathName
                downloadFile = input("Name of file to be downloaded: ")
                message = 'TYPE A'
                send(message)

                while True:
                    temp = receive()
                    temp = temp.decode()
                    temp = temp.split("'")
                    temp = temp[0].split(' ')
                    temp = temp[0]

                    if temp == '226':
                        message = 'ABOR'
                        combinedSendReceive(message)
                        receive()
                        break
                    else:
                        break

                retrieveFile(downloadFile)
                print(input("\nPress Enter"))
                

            if userInputSub == '2':
                os.path = pathName
                downloadFile = input("Name of file to be downloaded: ")
                message = 'TYPE I'
                send(message)

                while True:
                    temp = receive()
                    temp = temp.decode()
                    temp = temp.split("'")
                    temp = temp[0].split(' ')
                    temp = temp[0]

                    if temp == '226':
                        message = 'ABOR'
                        combinedSendReceive(message)
                        receive()
                        break
                    else:
                        break

                retrieveFile(downloadFile)
                print(input("\nPress Enter"))

            if userInputSub == "3":
                break
                

############ Send File ############

    if userInput == '4':
        while True:
            print("What type of file are you SENDING?")
            print("1: ASCII")
            print("2: Image")
            print('3: Go to main menu')
            
            userInputSub = input("Which type of file: ")

            if userInputSub == '1':
                os.path = pathName
                uploadFile = input("Name of file to be uploaded: ")
                send('TYPE A')

                while True:
                    temp = receive()
                    temp = temp.decode()
                    temp = temp.split("'")
                    temp = temp[0].split(' ')
                    temp = temp[0]

                    if temp == '226':
                        combinedSendReceive('ABOR')
                        break
                    else:
                        break

                sendFile(uploadFile)
                print(input("\nPress Enter"))
                

            if userInputSub == '2':
                os.path = pathName
                uploadFile = input("Name of file to be uploaded: ")
                send('TYPE I')

                while True:
                    temp = receive()
                    temp = temp.decode()
                    temp = temp.split("'")
                    temp = temp[0].split(' ')
                    temp = temp[0]

                    if temp == '226':
                        combinedSendReceive('ABOR')
                        break
                    else:
                        break

                sendFile(uploadFile)
                print(input("\nPress Enter"))
                
            if userInputSub == "3":
                break


############ Exit ############

    if userInput == 'EXIT':
        print('Exiting')
        send('QUIT')
        break

s.close()