import glob
import ipaddress
import json
import math
import socket
from _thread import start_new_thread
from socket import *
import time
import platform
import os
import sys

IP = 0


def setIP():
    global IP
    IP = str(input("Pleas Enter Your IPv4 Adress: \n"))


def tcpConnection():
    host = IP
    print(IP)
    serverPort = 8000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((host, serverPort))
    serverSocket.listen(5)

    while 1:
        connectionSocket, addr = serverSocket.accept()
        data = connectionSocket.recv(1024)
        currentTime = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
        data = data.decode()
        with open("serverLogs.txt", 'a') as f:
            f.write('Got connection from ' + str(addr) + " " + data + " " + currentTime + '\n')

        requestedFile = data
        OS = platform.system()
        currentPath = os.getcwd()

        if OS == "Windows":
            filename = currentPath + "\\files\\" + requestedFile
        else:
            filename = currentPath + "/files/" + requestedFile

        if os.path.exists(filename):
            size = str(os.path.getsize(filename))
            connectionSocket.send(size.encode())
            size = int(size)
            CHUNK_SIZE = math.ceil(math.ceil(size) / 5)
            index = 1

            answer = connectionSocket.recv(1024)
            answer = answer.decode()
            while 1:
                if os.path.exists(answer):
                    with open(answer, 'rb') as infile:
                        sendFile = infile.read()
                        connectionSocket.send(sendFile)
                        answer = connectionSocket.recv(1024)
                        answer = answer.decode()
                else:
                    break

            with open("serverLogs.txt", 'a') as f:
                f.write('Upload Complete' + " " + str(addr) + " " + requestedFile + " " + currentTime + '\n')

        else:
            respond = "File Not Found"
            with open("serverLogs.txt", 'a') as f:
                f.write(respond + " " + str(addr) + " " + data + " " + currentTime + '\n')
            connectionSocket.send(respond.encode())

        connectionSocket.close()
        f.close()


def p2pSendRequest(hostname, filename):
    hostname = str(hostname)
    serverName = hostname
    serverPort = 8000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    OS = platform.system()
    currentPath = os.getcwd()
    sentence = filename
    clientSocket.send(sentence.encode())
    if OS == "Windows":
        filename = currentPath + "\\files\\" + sentence
    else:
        filename = currentPath + "/files/" + sentence

    if OS == "Windows":
        filePATH = currentPath + "\\files\\"
    else:
        filePATH = currentPath + "/files/"

    respond = clientSocket.recv(1024)
    respond = respond.decode()

    if respond == "File Not Found":
        print("Requested File Not Found")
        currentTime = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
        with open("clientLogs.txt", 'a') as f:
            f.write('Requested File Not Found ' + str(clientSocket) + " " + sentence + " " + currentTime + '\n')
    else:
        filesize = int(respond)
        CHUNK_SIZE = math.ceil(math.ceil(filesize) / 5)
        for i in range(1, 6):
            dataFile = sentence + "_" + str(i)
            if not os.path.exists(dataFile):

                clientSocket.send(dataFile.encode())
                downloadedData = clientSocket.recv(CHUNK_SIZE)
                with open(dataFile, 'wb') as test:
                    test.write(downloadedData)
            else:
                print(-1)

        for i in range(1, 6):
            read_files = glob.glob(sentence + "*")

            with open(sentence, "wb") as outfile:
                for f in read_files:
                    with open(f, "rb") as infile:
                        outfile.write(infile.read())

            outfile.close()
            os.replace(currentPath + '\\' + sentence, filePATH + sentence)

        currentTime = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
        with open("clientLogs.txt", 'a') as f:
            f.write('Requested File Downloaded ' + str(clientSocket) + " " + sentence + " " + currentTime + '\n')
        outfile.close()


def UDPServer():
    UDPServer = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    UDPServer.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    UDPServer.settimeout(0.5)
    currentPath = os.getcwd()
    OS = platform.system()
    message = str()
    if OS == "Windows":
        filePATH = currentPath
    else:
        filePATH = currentPath
    try:
        if not os.path.exists(filePATH + "files"):
            os.mkdir("files")
    except FileExistsError:
        pass

    for file in os.listdir(filePATH):

        if file.endswith(("1", "2", "3", "4", "5")):
            message = message + ',' + str(file)

    while True:
        UDPServer.sendto(message.encode(), ('25.255.255.255', 5001))

        time.sleep(60)


def UDPClient():
    UDPClient = socket(AF_INET, SOCK_DGRAM)
    UDPClient.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    UDPClient.bind(("", 5001))
    result = {}
    while True:
        data, addr = UDPClient.recvfrom(1024)
        data = data.decode().split(",")
        key = str(addr)
        values = []
        for i in range(1, len(data)):
            values.append(data[i])

        result.update({key: values})

        a_file = open("package.json", "w")
        json.dump(result, a_file)


def main():
    a = str(input(
        "Please enter:\n1 to download \n2 to chunking file for upload \n3 to see available users with chunks\n"))
    if a == "1":
        while 1:
            dataName = str(input("Enter the file name or type exit for  return to main menu: "))
            if dataName == "exit":
                main()
            else:
                with open('package.json') as jsondata:
                    data = json.load(jsondata)
                    for ip in data:
                        newIP = str(ip).split(',')
                        newIP = newIP[0]
                        newIP = newIP.replace('(', '')
                        newIP = newIP.replace("'", '')
                        p2pSendRequest(newIP, dataName)




    elif a == "2":
        try:
            filename = str(input("Please write filename\n"))
            OS = platform.system()
            currentPath = os.getcwd()
            if OS == "Windows":
                path = currentPath + "\\files\\" + filename
            else:
                path = currentPath + "/files/" + filename

            size = int(os.path.getsize(path))
            CHUNK_SIZE = math.ceil(math.ceil(size) / 5)
            index = 1

            with open(path, 'rb') as infile:
                chunk = infile.read(int(CHUNK_SIZE))

                while chunk:
                    chunkname = filename + '_' + str(index)
                    with open(chunkname, 'wb+') as chunk_file:
                        chunk_file.write(chunk)
                    index += 1
                    chunk = infile.read(int(CHUNK_SIZE))
                    main()
        except FileNotFoundError:
            print("404 file does not exist. Check files and try again. Contact devs if the error persists... ",
                  sys.exc_info()[0])
            main()

    elif a == "3":
        with open('package.json') as f:
            test = json.load(f)
        print(json.dumps(test, indent=2))
        main()
    else:
        print("Wrong Input")
        main()


setIP()

start_new_thread(tcpConnection, ())
start_new_thread(UDPServer, ())
start_new_thread(UDPClient, ())
main()
