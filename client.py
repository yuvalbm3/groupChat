import select
import threading
from socket import *

nickname = input("Choose a nickname: ")


serverName = 'localhost'
serverPort = 55000
SERVER_ADDRESS = (serverName, serverPort)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(SERVER_ADDRESS)
private = False
download = False
list = []
menu = """Welcome to the chat!
        If you want to exit please type 'exit0'.
        For list of user who's connect type 'conn_list'.
        For sending message to certain connected user type 'privateMode'.
        For cancel the private mode type 'cancelPrivate'.
        For reaching to this menu type 'MENU'.
        """
print(menu)

def udp():
    num = list[0]
    size = list[1]
    udpclsock = socket(AF_INET, SOCK_DGRAM)                     #open UDP socket
    udpclsock.sendto(str(num).encode(), SERVER_ADDRESS)         #send the number of the wanted file to the server
    counter = 0                                                 #counter for the packets
    snum_list = [size]                                          #boolean list for aprove eche packet that arrive
    all_data = []                                               #list for all the data
    data, serverAdd = udpclsock.recvfrom(2048)
    data = data.decode('ascii')
    if data:
        print("File name:", data)
        file_name = data
    f = open(file_name, 'w')
    while True:
        print("udp8")
        ready = select.select([udpclsock], [], [], timeout)
        if ready[0] and counter < len(size):
            data, addr = udpclsock.recvfrom(2048)
            data = data.decode()
            i = data.index('-')                                 # '-' seperate between the data to the serial number
            serial_num = int(data[:i])
            all_data[serial_num] = data[i+1:]
            counter += 1
            snum_list[serial_num] = True
        else:
            for i in len(all_data):
                f.write(all_data[i])
            break


def main():
    global private
    while True:
        try:
            message = clientSocket.recv(1024).decode('ascii')                   #get messages from the server
            pc_agree = "~~Enter the number of the user you want to have private chat with."
            if message == "NAME":
                clientSocket.send(nickname.encode('ascii'))
            elif pc_agree in message:
                private = True
            elif len(list) >= 1 and "File size is:" in message:                 # get the size of the file and apply the UDP client
                print("in the way to udp")
                i = message.index(':')
                file_size = int(message[i+1:])
                list.append(file_size)
                udp()
            else:                                                               # if the message that get from the server is'nt saved, it would print to the screen
                print(message)
        except:
            print("Error. Closing the connection.")                             #if there is error the socket would get close
            clientSocket.close()
            break


def write():
    global download
    global private
    while True:
        inp = input("")
        if inp == "MENU":                           #print the menu
            print(menu)
        if inp == "exit0":                          #exit the program and sent message to the server to get him from the connect list
            clientSocket.send(inp.encode('ascii'))
            clientSocket.close()
            break
        elif inp == "conn_list":                    # to get the list of connected users
            clientSocket.send(inp.encode('ascii'))
        elif inp == "OK":
            clientSocket.send(inp.encode('ascii'))
        elif inp == "cancelPrivate":
            private = False
            clientSocket.send(inp.encode('ascii'))
        elif inp == "privateMode":                   # to apply privateMode
            private = True
            clientSocket.send(inp.encode('ascii'))
            print("~~Enter the serial number of the user you want to have private chat with.")
        elif private and inp.isnumeric():
            clientSocket.send(inp.encode('ascii'))
            private = False
        else:
            message = f'{nickname}: {inp}'
            clientSocket.send(message.encode('ascii'))


main_thread = threading.Thread(target=main)
main_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
write()
