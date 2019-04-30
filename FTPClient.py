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
    rec = s.recv(1024)
    # Returns the received value as a string
    return rec

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
    send('STOR' + fileName)
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
    passiveSocket((newIP, newPort))
    send('RETR '+ fileName)
    return receive()
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

pathName = ''