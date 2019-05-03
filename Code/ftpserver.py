import os
import socket
import stat
import sys
import threading
import time
from pathlib import Path
# from utils import fileProperty

#---------------------------------------------------- Socket Declaration ----------------------------------------------------#

try:
    host = socket.gethostbyname(socket.gethostname())
except socket.gaierror:
    host = socket.gethostname()

port = 21
working_directory  = os.getcwd()

#---------------------------------------------------- Client Declaration ----------------------------------------------------#

class FTPServerProtocol(threading.Thread):
    def __init__(self, command_socket, address):
        threading.Thread.__init__(self)
        self.authenticated      = False
        self.PASVmode          = False
        self.rest               = False
        self.allow_delete       = False
        self.working_directory  = working_directory
        self.base_path          = working_directory
        self.command_socket     = command_socket
        self.address            = address
        self.type               = 'A'
        self.mode               = 'S'
        self.file_structure     = 'F'

    def run(self):                                                                                                          # Executes commands recieved by user
        self.sendResponse('220' + 'Service ready for new user.\r\n')    
        while True:
            try:
                data = self.command_socket.recv(1024).rstrip()                                                              #1024 acts as a ascii buffer
                try:
                    client_command = data.decode('utf-8')
                except AttributeError:
                    client_command = data
                print('Received data', client_command)
                if not client_command:
                    break
            except socket.error as error:
                print('Receive', error)

            try:
                client_command, param = client_command[:4].strip().upper(), client_command[4:].strip() or None
                func = getattr(self, client_command)
                func(param)
            except AttributeError as error:
                self.sendResponse('500 Syntax error, unrecognized command.\r\n')
                print('Receive', error)

    #---------------------------------------------------- FTP transmission functions ----------------------------------------------------#

    def createDataSocket(self):
        # Open socket with client for data transmission
        print('createDataSocket', 'Opening a data channel')
        try:
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.PASVmode:
                self.data_socket, self.address = self.server_socket.accept()

            else:
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((self.data_socket_address, self.data_socket_port))
        except socket.error as error:
            print('createDataSocket', error)
    
    def generatePath(self, base_path='', working_path=''):
        print(base_path + working_path)
        return base_path + working_path

    def terminateDataSocket(self):
        # Close data tranmission socket with client
        print('terminateDataSocket', 'Closing a data channel')
        try:
            self.data_socket.close()
            if self.PASVmode:
                self.server_socket.close()
        except socket.error as error:
            print('terminateDataSocket', error)

    def sendResponse(self, client_command):
        # Transmit request codes and relevant message to client
        self.command_socket.send(client_command.encode('utf-8'))

    def sendData(self, data):
        # Transmit file data to client
        if self.type == 'I':
            self.data_socket.send(data)
        else:
            self.data_socket.send(data.encode('utf-8'))

    #---------------------------------------------------- FTP command functions ----------------------------------------------------#
    
    def USER(self, username):
        # Lets user to set their username
        print("USER", username)
        if not username:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')
        else:
            self.sendResponse('331 User name okay, need password.\r\n')
            self.username = username
            path = self.working_directory + '\\' + username

            try:
                os.mkdir(path)
            except OSError:
                pass

            path = path.split('\\')
            user_path_index = path.index(username)
            base_path = path[:user_path_index]
            working_path = path[user_path_index:]
            self.base_path = '\\'.join(base_path)
            self.working_directory = '\\' + '\\'.join(working_path) + '\\'

    def PASS(self, password):
        # Lets user to set their password
        print("PASS", password)
        if not password:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

        elif not self.username:
            self.sendResponse('503 Bad sequence of commands.\r\n')

        else:
            self.sendResponse('230 User logged in, proceed.\r\n')
            self.password = password
            self.authenticated = True
            self.allow_delete = True

    def TYPE(self, type):
        # Specify file mode to be handled
        print('TYPE', type)
        self.type = type

        if self.type == 'I':
            self.sendResponse('200 Binary file mode.\r\n')
        elif self.type == 'A':
            self.sendResponse('200 Ascii file mode.\r\n')
        else:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

    def PASV(self, client_command):
        # Makes server-DTP "listen" on a non-default data port to wait for a connection rather than initiate one upon receipt of a transfer command
        print("PASV", client_command)
        self.PASVmode  = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, 0))
        self.server_socket.listen(5)
        address, port = self.server_socket.getsockname()
        self.sendResponse('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(address.split('.')), port>>8&0xFF, port&0xFF))

    def MODE(self, mode):
        # Specifies data transfer mode for server
        print('MODE', mode)
        self.mode = mode

        if self.mode == 'S':
            self.sendResponse('200 Stream transfer mode.\r\n')
        elif self.mode == 'B':
            self.sendResponse('502 Command not implemented.\r\n')
        elif self.mode == 'C':
            self.sendResponse('502 Command not implemented.\r\n')
        else:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

    def PORT(self, client_command):
        # Specify the port to be used for data transmission
        print("PORT: ", client_command)
        if self.PASVmode:
            self.server_socket.close()
            self.PASVmode = False

        connection_info = client_command[5:].split(',')
        self.data_socket_address = '.'.join(connection_info[:4])
        self.data_socket_port = (int(connection_info[4])<<8) + int(connection_info[5])
        self.sendResponse('200 Get port.\r\n')

    def LIST(self, directory_path):
        # Sends list of content in specified server path
        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
            return

        if not directory_path:
            server_path = os.path.abspath(os.path.join(self.base_path + self.working_directory, '.'))
        elif directory_path.startswith(os.path.sep):
            server_path = os.path.abspath(directory_path)
        else:
            server_path = os.path.abspath(os.path.join(self.base_path + self.working_directory, '.'))

        print('LIST', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        elif not os.path.exists(server_path):
            self.sendResponse('550 LIST failed Path name not exists.\r\n')
        else:
            self.sendResponse('150 Here is listing.\r\n')
            self.createDataSocket()

            # if not os.path.isdir(server_path):
            #     fileMessage = fileProperty(server_path)
            #     self.data_socket.sock(fileMessage+'\r\n')
            # else:
            #     for file in os.listdir(server_path):
            #         fileMessage = fileProperty(os.path.join(server_path, file))
            #         self.sendData(fileMessage+'\r\n')

            self.terminateDataSocket()
            self.sendResponse('226 List done.\r\n')

    def CWD(self, directory_path):
        # Allows user to change current directory to a new directory on the server
        server_path = self.base_path + directory_path
        print('CWD', server_path)

        if not os.path.exists(server_path) or not os.path.isdir(server_path):
            self.sendResponse('550 CWD failed Directory does not exist.\r\n')
            return

        self.working_directory = directory_path

        self.sendResponse('250 CWD Command successful.\r\n')

    def PWD(self, client_command):
        # Returns the current server directory path
        print('PWD', client_command)
        self.sendResponse('257 "%s".\r\n' % self.working_directory)

    def CDUP(self, client_command):
        # Changes current working directory to parent directory
        if self.working_directory != '\\' + self.username:
            self.working_directory = '\\' + os.path.abspath(os.path.join(self.base_path + self.working_directory, '..'))
        print('CDUP', self.working_directory)
        self.sendResponse('200 OK.\r\n')

    # def DELE(self, filename):
    #     # Deletes file specified in the pathname to be deleted at the server site
    #     server_path = self.generatePath(self.base_path, filename)

    #     print('DELE', server_path)

    #     if not self.authenticated:
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
    #     server_path = self.generatePath(self.base_path, dirname)
    #     print('MKD', server_path)

    #     if not self.authenticated:
    #         self.sendResponse('530 User not logged in.\r\n')
    #     else:
    #         try:
    #             os.mkdir(server_path)
    #             self.sendResponse('257 Directory created.\r\n')
    #         except OSError:
    #             self.sendResponse('550 MKD failed. Directory "%s" already exists.\r\n' % server_path)

    def RMD(self, dirname):
        # Removes specified directory at current path directory
        import shutil
        server_path = self.generatePath(self.base_path, dirname)
        print('RMD', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        elif not self.allow_delete:
            self.sendResponse('450 Invalid permissions.\r\n')
        elif not os.path.exists(server_path):
            self.sendResponse('550 RMDIR failed Directory "%s" not exists.\r\n' % server_path)
        else:
            shutil.rmtree(server_path)
            self.sendResponse('250 Directory deleted.\r\n')

    def REST(self, pos):
        # Represents the server marker at which file transfer is to be restarted
        self.pos  = int(pos)
        print('REST', self.pos)
        self.rest = True
        self.sendResponse('250 File position reset.\r\n')

    def RETR(self, filename):
        # Causes server-DTP to transfer a copy of the file, specified in the pathname, to the server- or user-DTP at the other end of the data connection
        server_path = self.generatePath(self.base_path, "\\" + filename)
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

    def STOR(self, filename):
        # Causes the server-DTP to accept the data transferred via the data connection and to store the data as a file at the server site
        if not self.authenticated:
            self.sendResponse('530 STOR failed. User is not logged in.\r\n')
            return

        server_path = self.generatePath(self.base_path, "\\" + filename)
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
                data = self.data_socket.recv(4194304)
            else:
                data = self.data_socket.recv(4194304).decode('utf-8')

            if not data:
                break

            file.write(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer completed.\r\n')

    def NOOP(self, client_command):
        # Specifies no action other than that the server send an OK reply
        print('NOOP', client_command)
        self.sendResponse('200 OK.\r\n')

    def HELP(self, param):
        # Provides server command list to client
        print('HELP', param)
        help = """
            214
            USER [name], Its argument is used to specify the user's string. It is used for user authentication.
            PASS [password], Its argument is used to specify the user password string.
            TYPE [type], Its argument is used to specify the file type.
            PASV The directive requires server-DTP in a data port.
            MODE [mode], Its argument is used to specify the data transfer type.
            STRU [structure], Its argument is used to specify the file structure.
            PORT [h1, h2, h3, h4, p1, p2], The command parameter is used for the data connection data port
            LIST [directory_path or filename], This command allows the server to send the list to the passive DTP.
                 If the pathname specifies a path or The other set of files, the server sends a list of files in
                 the specified directory. Current information if you specify a file path name, the server will
                 send the file.
            NLST [directory_path or filename], This command calls LIST with the provided argument.
            CWD  [path], Its argument is used to specify a new working directory.
            PWD  Get current working directory.
            CDUP Changes the working directory on the remote host to the parent of the current directory.
            DELE [filename], Its argument is used to specify the file to be deleted.
            MKD  [directory_name] Its argument is used to create the directory specified in the RemoteDirectory
                 parameter on the remote host.
            RNFR [old name], Its argument is used to specify the file to be renamed (RNTO must follow).
            RNTO [new name] Its argument is used to specify the new name of the file to be renamed (from RNFR).
            REST [position] Marks the beginning (REST) ​​The argument on behalf of the server you want to re-start
                 the file transfer. This command and Do not send files, but skip the file specified data checkpoint.
            RETR This command allows server-FTP send a copy of a file with the specified path name to the data
                 connection on the other end.
            STOR This command allows server-DTP to receive data transmitted via a data connection, and data is
                 stored as a file on the server site.
            APPE This command allows server-DTP to receive data transmitted via a data connection, and data is stored
                 as A file server site.
            SYST This command is used to find the server's operating system type.
            NOOP This command executes no action other than prompting a 200 OK response from the server.
            HELP Displays help information.
            QUIT This command terminates a user, if not being executed file transfer, the server will shut down
                 Control connection\r\n.
            """
        self.sendResponse(help)

    def QUIT(self, param):
        # Connected user logs out and disconnects from server if not transfer in progress
        print('QUIT', param)
        self.sendResponse('221 Goodbye.\r\n')

def serverListener():
    global listen_socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((host, port))
    listen_socket.listen(5)

    print('Server started', 'Listen on: %s, %s' % listen_socket.getsockname())
    while True:
        connection, address = listen_socket.accept()
        ftp_connection_instance = FTPServerProtocol(connection, address)
        ftp_connection_instance.start()
        print('Accept', 'Created a new connection %s, %s' % address)

if __name__ == "__main__":
    print('FTP server started\r\n')
    listener = threading.Thread(target=serverListener)
    listener.start()

    if input().lower() == "end":
        listen_socket.close()
        print('Server stopped', 'Server closed')
        sys.exit()
