import threading
from datetime import time
from socket import *
import os                    #to get the size of the file
import math
SERVER_ADDRESS = ('', 55000)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(SERVER_ADDRESS)
serverSocket.listen(5)

clients_Addr = []
clients = []
nicknames = []
pchat = []                              #list of users in the private chat
files = ['200.txt', '100.txt']
stop_download = [False]


def broadcast(message):                 #send message to broadcast
    for c in clients:
        c.send(message)


def pchatf(message, bool):              #send messages only to people in the pchat list
    if bool == 0:                       #for system messages
        for p in pchat:
            p.send(message.encode('ascii'))
    if bool == 1:                       # for messages between the pchat members
        msm = "--p--  " + message
        for p in pchat:
            p.send(msm.encode('ascii'))


def private_message(client, message):
    client.send(message.encode('ascii'))


def chat4two(client, num):
    index = clients.index(client)
    if len(pchat) > 0:
        pchat.clear()
    pchat.append(client)
    pchat.append(clients[num-1])
    if client == clients[num-1] and len(pchat) == 2:                        # you can't be alon in pchat
        private_message(client, "~~You can't open private chat alone. Sorry.\n")
        pchat.clear()
    else:                                                                   #ask the other user if he want to enter the private chat
        private_message(clients[num-1], f"~~{nicknames[index]} want to creat private chat with you.\n If you agree type 'OK', else type 'cancelPrivate'\n")


def print_clients(client, bool):                    #print the list of connected clients
    message = "~~Users connect to the server:\n"
    for c in range(len(nicknames)):
        message += f"\t {c+1}. {nicknames[c]} \n"
    client.send(message.encode('ascii'))
    if bool == 1:                                   #if the bool is 1, the user can ask one from the list to enter to the private chat
        private_message(client, "~~Enter the number of the user you want to have private chat with.")


def print_files(client, bool):                      # print the list of files in the server
    message = "~~ Files that are available to download from the server:\n"
    for c in range(len(files)):
        message += f"\t {c+1}. {files[c]} \n"
    client.send(message.encode('ascii'))
    if bool == 1:
        private_message(client, "~~Enter the number of the file you want to download.")


def download_files():                           #open udp server
    buf = 2048
    udpservsock = socket(AF_INET, SOCK_DGRAM)   #open socket
    udpservsock.bind(("", 55000))
    print("Server is ready..")
    message, clientAddress = udpservsock.recvfrom(2048)
    message = message.decode('ascii')           #first mesage is the num of the file is requested
    print(message)
    file_name = files[int(message)]
    print(file_name)
    udpservsock.sendto(file_name.encode('ascii'), clientAddress)
    print(f"~~ download | {file_name}")
    serial_number = 0
    data_order = []
    with open(file_name, "r") as f:
        while True:
            data = f.read(buf - 10)
            if not data:
                break
            data_order.append((str(serial_number) + '-' + data))
            udpservsock.sendto(data_order[serial_number].encode('ascii'), clientAddress)
            serial_number += 1
    udpservsock.close()
    f.close()

def handle(client):
    download = False
    flag = False
    private = False
    channel = False
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == "exit0":
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'~~{nickname} left the chat!'.encode('ascii'))
                nicknames.remove(nickname)
                break
            elif message == "DOWNLOAD":
                print("in download")
                private = False
                flag = False
                channel = False
                download = True
                print_files(client, 1)
            elif download and message.isnumeric():
                print("in download and num")
                num = int(message)
                if num < 0 or num > len(files):
                    download = False
                    private_message(client, "!~~Such file not exist. Try again")
                else:
                    f_bsize = os.path.getsize(f'{files[num]}')          # number of byte in the file
                    f_psize = int(math.ceil(f_bsize / 2038))            # number of packets that need to be sent
                    print(f_psize)
                    print(f_bsize)
                    client.send(f'File size is:{f_psize}'.encode('ascii'))
                    download_files()
                    download = False
            elif download and message == "CONTINUE_D":
                stop_download.clear
                stop_download.append(False)
            elif download and message == "CANCEL_D":
                stop_download.clear
                stop_download.append(True)
            elif message == "conn_list":
                print_clients(client, 0)
            elif message == "privateMode":
                private = True
                print_clients(client, 1)
            elif message == "cancelPrivate":
                if not private:
                    private = False
                    flag = False
                    channel = False
                    pchatf("~~~The private mode is off. All the users could see your messages from now on.", 0)
                    pchat.clear()
                else:
                    private = False
                    channel = False
                    flag = False
                    pchatf("~~~The private mode decline. All the users could see your messages from now on.", 0)
                    pchat.clear()
            elif private and flag and message == "OK":
                channel = True
                pchatf("~~Your private chat is open...", 0)
            elif message == "OK" and client in pchat and not private and not flag:
                channel = True
                flag = True
                private = True
                pchatf("~~Your private chat is open...", 0)
            elif private and flag and channel and len(pchat) != 0:
                pchatf(message, 1)
            elif private and message.isnumeric():
                print(len(clients))
                if int(message) > len(clients) or int(message) <= 0:
                    message = "!~~There isn't such user try again."
                    private_message(client, message)
                    private = False
                    pchat.clear()
                else:
                    channel = True
                    flag = True
                    chat4two(client, int(message))
            else:
                print("nonono")
                broadcast(message.encode('ascii'))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'~~{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break


def main():
    while True:
        connectionSocket, addrClient = serverSocket.accept()
        print(f'connected with {str(addrClient)}')

        connectionSocket.send('NAME'.encode('ascii'))
        nickname = connectionSocket.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(connectionSocket)
        clients_Addr.append(addrClient)
        print(f'~~The client nickname is {nickname}')
        broadcast(f'~~{nickname} joined the chat!'.encode('ascii'))
        connectionSocket.send('~~Connected to the server!'.encode('ascii'))

        handle_thread = threading.Thread(target=handle, args=(connectionSocket,))
        handle_thread.start()

        download_thread = threading.Thread(target=download_files())
        download_thread.start()


print("The server is ready to receive client")
main()
serverSocket.close()
