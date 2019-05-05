import os
import socket
import threading
import sys
import time
import stat
from pathlib import Path

#---------------------------------------------------- Socket Declaration ----------------------------------------------------#

try:
    host = socket.gethostbyname(socket.gethostname())
except socket.gaierror:
    host = socket.gethostname()

port = 21
rootDirectory  = os.getcwd()

#---------------------------------------------------- Client Declaration ----------------------------------------------------#

class FTPServerProtocol(threading.Thread):
    def __init__(self, connectionControlSocket, clientAddress):
        threading.Thread.__init__(self)
        self.loginStatus                = False
        self.PASVmode                   = False
        self.rest                       = False
        self.delete                     = False
        self.rootDirectory              = rootDirectory
        self.userDirectory              = rootDirectory
        self.connectionControlSocket    = connectionControlSocket
        self.clientAddress              = clientAddress
        self.type                       = 'A'
        self.mode                       = 'S'

    def run(self):   # Executes commands recieved by user                                                                                                       
        self.sendResponse('220' + 'Service ready for new user.\r\n')    
        while True:
            try:
                data = self.connectionControlSocket.recv(1024).rstrip() #1024 acts as a ascii buffer                                                         
                try:
                    command = data.decode('utf-8')
                except AttributeError:
                    command = data
                print('Received data', command)
                if not command:
                    break
            except socket.error as error:
                print('Receive', error)

            try:
                command, param = command[:4].strip().upper(), command[4:].strip() or None
                func = getattr(self, command)
                func(param)
            except AttributeError as error:
                self.sendResponse('500 Syntax error, unrecognized command.\r\n')
                print('Receive', error)

    #---------------------------------------------------- FTP transmission functions ----------------------------------------------------#

    def createDataSocket(self): # Open data transmission socket
        print('createDataSocket', 'Creating data channel')
        try:
            self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.PASVmode:
                self.dataSocket, self.clientAddress = self.server_socket.accept()

            else:
                self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dataSocket.connect((self.data_socket_address, self.data_socket_port))
        except socket.error as error:
            print('createDataSocket', error)
    
    def generatePath(self, userDirectory='', working_path=''):
        print(userDirectory+ working_path)
        return userDirectory+ working_path

    def terminateDataSocket(self): # Terminate data tranmission socket 
        print('terminateDataSocket', 'Terminating data channel')
        try:
            self.dataSocket.close()
            if self.PASVmode:
                self.server_socket.close()
        except socket.error as error:
            print('terminateDataSocket', error)

    def sendResponse(self, command): # Send response code to client
        self.connectionControlSocket.send(command.encode('utf-8'))

    def sendData(self, data): # Send file data to client
        if self.type == 'I':
            self.dataSocket.send(data)
        else:
            self.dataSocket.send(data.encode('utf-8'))

    #---------------------------------------------------- FTP COMMANDS ----------------------------------------------------#

    #----------------------------------------------- ACCESS CONTROL COMMANDS -----------------------------------------------#
    
    def USER(self, username): # Identification of user name
        print("USER", username)
        if not username:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')
        else:
            self.sendResponse('331 User name okay, need password.\r\n')
            self.username = username
            path = self.rootDirectory + '\\' + username

            try:
                os.mkdir(path)
            except OSError:
                pass

            path = path.split('\\')
            user_path = path.index(username)
            userDirectory = path[:user_path]
            working_path = path[user_path:]
            self.userDirectory = '\\'.join(userDirectory)
            self.rootDirectory = '\\' + '\\'.join(working_path) + '\\'

    def PASS(self, password): # Identification of password
        print("PASS", password)
        if not password:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

        elif not self.username:
            self.sendResponse('503 Bad sequence of commands.\r\n')

        else:
            self.sendResponse('230 User logged in, proceed.\r\n')
            self.password = password
            self.loginStatus = True
            self.delete= True

    def CWD(self, directory_path): # Changes working directory on server
        server_path = self.userDirectory+ directory_path
        print('CWD', server_path)

        if not os.path.exists(server_path) or not os.path.isdir(server_path):
            self.sendResponse('550 CWD failed Directory does not exist.\r\n')
            return

        self.rootDirectory = directory_path

        self.sendResponse('250 CWD Command successful.\r\n')

    def CDUP(self, command): # Changes root directory to home directory
        if self.rootDirectory != '\\' + self.username:
            self.rootDirectory = '\\' + os.path.abspath(os.path.join(self.userDirectory + self.rootDirectory, '..'))
        print('CDUP', self.rootDirectory)
        self.sendResponse('200 OK.\r\n')

    def QUIT(self, param): # Terminates user connection
        print('QUIT', param)
        self.sendResponse('221' + 'Service closing control connection.\r\n')

    #---------------------------------------------------------------------- TRANSFER PARAMETER COMMANDS ----------------------------------------------------------------#

    def PORT(self, command): # Specify the port number used for data transmission
        print("PORT: ", command)
        if self.PASVmode:
            self.server_socket.close()
            self.PASVmode = False

        connection_info = command[5:].split(',')
        self.data_socket_address = '.'.join(connection_info[:4])
        self.data_socket_port = (int(connection_info[4])<<8) + int(connection_info[5])
        self.sendResponse('200 OK.\r\n')

    def PASV(self, command): # Initiates passive mode by default
        print("PASV", command)
        self.PASVmode  = True #sets passive mode to active
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, 0))
        self.server_socket.listen(5)
        clientAddress, port = self.server_socket.getsockname()
        self.sendResponse('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(clientAddress.split('.')), port>>8&0xFF, port&0xFF))

    def TYPE(self, type): # Specify file type to be transmitted
        print('TYPE', type)
        self.type = type

        if self.type == 'I':
            self.sendResponse('200 OK: Binary file mode.\r\n')
        elif self.type == 'A':
            self.sendResponse('200 OK: Ascii file mode.\r\n')
        else:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

    def MODE(self, mode): # Selects mode for data transfer
        print('MODE', mode)
        self.mode = mode

        if self.mode == 'S':
            self.sendResponse('200 Stream transfer mode.\r\n')
        elif self.mode == 'C':
            self.sendResponse('502 Command not implemented.\r\n')
        elif self.mode == 'B':
            self.sendResponse('502 Command not implemented.\r\n')
        else:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

    #---------------------------------------------------------------------- FTP SERVICE COMMANDS ----------------------------------------------------------------#

    def RETR(self, filename): #Retrieve file from path destination
        server_path = self.generatePath(self.userDirectory, "\\" + filename)
        print('RETR', server_path)

        if not os.path.exists(server_path):
            return
        try:
            if self.type=='I':
                file = open(server_path, 'rb')
            else:
                file = open(server_path, 'r')
        except OSError as error:
            print('RETR', error)

        self.sendResponse('150 Opening data connection.\r\n')

        if self.rest:
            file.seek(self.pos)
            self.rest = False

        self.createDataSocket()

        while True:
            data = file.read(4194304)
            if not data: break
            if self.mode == 'S':
                self.sendData(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer complete.\r\n')

    def STOR(self, filename): #Accepts data transferred by data connection
        if not self.loginStatus:
            self.sendResponse('530 STOR failed. User is not logged in.\r\n')
            return

        server_path = self.generatePath(self.userDirectory, "\\" + filename)
        print('STOR', server_path)

        try:
            if self.type == 'I':
                file = open(server_path, 'wb')
            else:
                file = open(server_path, 'w')
        except OSError as error:
            print('STOR', error)

        self.sendResponse('150 Opening data connection.\r\n' )
        self.createDataSocket()

        while True:
            if self.type == 'I':
                data = self.dataSocket.recv(4194304)
            else:
                data = self.dataSocket.recv(4194304).decode('utf-8')

            if not data:
                break

            file.write(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer completed.\r\n')

    def PWD(self, command): # Returns current server directory path
        print('PWD', command)
        self.sendResponse('257 "%s".\r\n' % self.rootDirectory)

    def LIST(self, directory_path): # List file contents in given repository
        if not self.loginStatus:
            self.sendResponse('530 User not logged in.\r\n')
            return

        if not directory_path:
            server_path = os.path.abspath(os.path.join(self.userDirectory + self.rootDirectory, '.'))
        elif directory_path.startswith(os.path.sep):
            server_path = os.path.abspath(directory_path)
        else:
            server_path = os.path.abspath(os.path.join(self.userDirectory + self.rootDirectory, '.'))

        print('LIST', server_path)

        if not self.loginStatus:
            self.sendResponse('530 Not logged in.\r\n')
        elif not os.path.exists(server_path):
            self.sendResponse('550 File unavailable.\r\n')
        else:
            self.sendResponse('150 File status okay; about to open data connection.\r\n')
            self.createDataSocket()
            self.terminateDataSocket()
            self.sendResponse('226 Closing data connection.\r\n')

    def NOOP(self, command): #Ping Test
        print('NOOP', command)
        self.sendResponse('200 OK.\r\n')



def serverListener():
    global controlSocket
    controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    controlSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    controlSocket.bind((host, port))
    controlSocket.listen(5) #Waits for client connection (passive mode)

    print('Listening on: %s, %s' % controlSocket.getsockname())
    while True:
        connection, clientAddress = controlSocket.accept()
        FTPconnection = FTPServerProtocol(connection, clientAddress) 
        FTPconnection.start()
        print('Accept', 'Connection created %s, %s' % clientAddress)

if __name__ == "__main__":
    print('FTP server initialized\r\n')
    listener = threading.Thread(target=serverListener)
    listener.start()

    if input().lower() == "end":
        controlSocket.close()
        print('FTP server terminated')
        sys.exit()

#-------------------------------------------- Not required on client side ----------------------------------------------------------------

    # def DELE(self, filename):
    #     # Deletes file specified in the pathname to be deleted at the server site
    #     server_path = self.generatePath(self.userDirectory, filename)

    #     print('DELE', server_path)

    #     if not self.loginStatus:
    #         self.sendResponse('530 User not logged in.\r\n')
    #     elif not os.path.exists(server_path):
    #         self.send('550 DELE failed File %s does not exist\r\n' % server_path)
    #     elif not self.allow_delete:
    #         self.send('450 DELE failed delete not allowed.\r\n')
    #     else:
    #         os.remove(server_path)
    #         self.sendResponse('250 File deleted.\r\n')

    # def MKD(self, dirname):
    #     # Creates specified directory at current path directory
    #     server_path = self.generatePath(self.userDirectory, dirname)
    #     print('MKD', server_path)

    #     if not self.loginStatus:
    #         self.sendResponse('530 User not logged in.\r\n')
    #     else:
    #         try:
    #             os.mkdir(server_path)
    #             self.sendResponse('257 Directory created.\r\n')
    #         except OSError:
    #             self.sendResponse('550 MKD failed. Directory "%s" already exists.\r\n' % server_path)

    # def RMD(self, dirname):
    # server_path = self.generatePath(self.userDirectory, dirname)
    # print('RMD', server_path)

    # if not self.loginStatus:
    #     self.sendResponse('530 User not logged in.\r\n')
    # elif not self.delete:
    #     self.sendResponse('450 Invalid permissions.\r\n')
    # elif not os.path.exists(server_path):
    #     self.sendResponse('550 RMDIR failed Directory "%s" not exists.\r\n' % server_path)
    # else:
    #     shutil.rmtree(server_path)
    #     self.sendResponse('250 Directory deleted.\r\n')