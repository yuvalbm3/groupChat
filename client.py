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
all_data = []                               # list for all the data
list = []
menu = """Welcome to the chat!
        If you want to exit please type 'exit0'.
        For list of user who's connect type 'conn_list'.
        For sending message to certain connected user type 'privateMode'.
        For cancel the private mode type 'cancelPrivate'.
        For reaching to this menu type 'MENU'.
        """
print(menu)

# def openUDP():
#     print("U1")
#     sock = socket(AF_INET, SOCK_DGRAM)
#     print("U2")
#     # sock.bind(SERVER_ADDRESS)
#     print("U3")
#     clientSocket.send(str(SERVER_ADDRESS).encode('ascii'))
#     conti(sock)
#
#
# def conti(sock):
#     print(f"1the len is:{len(download)}")
#     print("U4")
#     counter = 0
#     size = download[1]
#     print("U5")
#     all_data = [size]
#     print("U6")
#     while True:
#         print(f"2the len is:{len(download)}")
#         print(download[2])
#         c_addr = download[2]
#         data, c_addr = sock.recvfrom(2048)
#         print("U7b")
#         if data:
#             print("U7c")
#             print("File name:", data)
#             file_name = data.strip()
#         print("U8")
#         f = open(file_name, 'w')
#         print("U9")
#         while True:
#             print("U10")
#             ready = select.select([sock], [], [], timeout)
#             print("U11")
#             if ready[0] and counter < len(size):
#                 print("U12")
#                 data, addr = sock.recvfrom(2048)
#                 print("U13")
#                 i = data.index('-')
#                 print("U14")
#                 serial_num = int(data[:i])
#                 print("U15")
#                 all_data[serial_num] = data[i+1:]
#                 print("U16")
#                 counter += 1
#                 print("U17")
#             else:
#                 print("U18")
#                 for i in len(all_data):
#                     print("U19")
#                     f.write(all_data[i])
#                     print("U20")
#                 break


def udp():      #for donwload function
    global all_data
    num = list[0]
    size = list[1]
    udpclsock = socket(AF_INET, SOCK_DGRAM)                     #open UDP socket
    udpclsock.bind(SERVER_ADDRESS)
    udpclsock.sendto(str(num).encode(), SERVER_ADDRESS)         #send the number of the wanted file to the server
    counter = 0                                                 #counter for the packets
    snum_list = [size]                                          #boolean list for aprove eche packet that arrive
    data, serverAdd = udpclsock.recvfrom(2048)      #get the file name to data
    data = data.decode('ascii')
    if data:
        print("File name:", data)
        file_name = f'copy_{data}'
    f = open(file_name, 'w')
    while True and download:
        # print("udp8")
        ready = select.select([udpclsock], [], [], timeout)         #first list is readable, second list is writeable and third list is expectional
        # print("udp9")
        if ready[0] and counter < len(size):
            data, addr = udpclsock.recvfrom(2048)       #recieve the data
            data = data.decode()
            i = data.index('-')                                 # '-' seperate between the serial number to the data
            serial_num = int(data[:i])                          # get the serial number from the data from index 0 to index i
            all_data[serial_num] = data[i+1:]
            counter += 1                                        # counter check we are not out of limits
            snum_list[serial_num] = True                        # add True to the boolean list in index serial number
            # for i in len(snum_list):                            #selctive repeat
            #     if snum_list[i] == False:
            #         udpclsock.sendto(f'{i}'.encode(), SERVER_ADDRESS)
        else:
            for i in len(all_data):
                f.write(all_data[i])
                print("Download completed!")
            break
    udpclsock.close()
    f.close()


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
                print(message[i+1])
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
        elif inp == "DOWNLOAD":                     # download files from the server
            private = False
            download = True
            clientSocket.send(inp.encode('ascii'))
        elif inp == "CONTINUE_D":                   #continue downloading, function isn't working
            clientSocket.send(inp.encode('ascii'))
        elif inp == "CANCEL_D":                     #cancelthe download, function isn't working
            download = False
            all_data.clear()
            clientSocket.send(inp.encode('ascii'))
        elif download and inp.isnumeric():          #if the boolean download is True and the input is number
            num = int(inp) - 1                      #the list of file begin in 1 not 0
            private = False
            list.append(num)
            clientSocket.send(str(num).encode('ascii'))
        elif inp == "OK":
            clientSocket.send(inp.encode('ascii'))
        elif inp == "cancelPrivate":
            private = False
            clientSocket.send(inp.encode('ascii'))
        elif inp == "privateMode":                   # to apply privateMode
            private = True
            clientSocket.send(inp.encode('ascii'))
            #print("~~Enter the serial number of the user you want to have private chat with.")
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
