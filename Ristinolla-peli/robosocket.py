#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import numpy as np
import operator
from time import sleep

HOST = "192.168.100.57"
PORT = 30002
coordinates = []

# Järjestelee robotilta saadun 2d taulukon samaan järjestykseen kuin pelissä käytetään
def SortArray(array):

    array = sorted(array, key = operator.itemgetter(0), reverse = True) #lambda k: [k[0], k[1]])
    sortedArrayTemp = []
    sortedArray = []

    for i in range(3):
        sortedArrayTemp.append(array[0+i*3])
        sortedArrayTemp.append(array[1+i*3])
        sortedArrayTemp.append(array[2+i*3])

        sortedArrayTemp = sorted(sortedArrayTemp, key = operator.itemgetter(1), reverse = True)

        sortedArray.append(sortedArrayTemp[0])
        sortedArray.append(sortedArrayTemp[1])
        sortedArray.append(sortedArrayTemp[2])

        sortedArrayTemp = []


    OffsetCalc(sortedArray, 0, 0)

    return sortedArray


def OffsetCalc(sortedArray, middleX, middleY):

    x = float(middleX) # float(sortedArray[4][0]) #
    y = float(middleY) # float(sortedArray[4][1]) #
    dist = 71.0/1000.0 # Etäisyys seuraavaan ruutuun

    # Vasen yläkulma
    sortedArray[0][0] = x + dist#- dist
    sortedArray[0][1] = y + dist

    # Keski ylä
    sortedArray[1][0] = x
    sortedArray[1][1] = y + dist

    # Oikea yläkulma
    sortedArray[2][0] = x - dist#+ dist
    sortedArray[2][1] = y + dist


    # Vasen keski
    sortedArray[3][0] = x + dist#- dist
    sortedArray[3][1] = y

    # Oikea Keski
    sortedArray[5][0] = x - dist#+ dist
    sortedArray[5][1] = y


    # Vasen alakulma
    sortedArray[6][0] = x + dist#- dist
    sortedArray[6][1] = y - dist

    # Keski ala
    sortedArray[7][0] = x
    sortedArray[7][1] = y - dist

    # Oikea alakulma
    sortedArray[8][0] = x - dist#+ dist
    sortedArray[8][1] = y - dist

    # Keski
    sortedArray[4][0] = x
    sortedArray[4][1] = y

    return sortedArray


# Palauttaa taulukon, jossa on robotin koordinaatit jokaiselle pelin ruudulle
def GetCoordinates(s, c):

    global coordinates
    count = 0
    try:
        while(count < 1000): # yritetään kunnes saadaan yhteys päälle
            count += 1

            msg = c.recv(1024)
            print msg
            sleep(1)
            if msg == "sending_coordinates":
                coordinates = []
                value = "asd"
                arrayCounter = 0
                while value != "end":
                    value = c.recv(1024)
                    if (value != 'end'):
                        coordinates.append(value)
                    arrayCounter += 1

                middleX = float(coordinates[0])
                middleY = float(coordinates[1])

                coordinates = np.zeros((9, 6)) #[[]*9 for x in xrange(2)]
                coordinates = OffsetCalc(coordinates, middleX, middleY)

                return #coordinates
            else:
                print ("Not asking for data")

    except KeyboardInterrupt:
        sys.exit(1)


# Vastaanottaa UR5:ltä pelialustan tiedot, jotta tiedetään esim miten pelaaja on liikkunut.
def ReceiveBoard( s, c):
    board = np.array([[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]])
    value = "asd"

    try:
        while(True):
            msg = c.recv(1024)
            print("saatu viesti", msg, "loppu")
            if msg == "sending_board":

                place = 0
                while value != "end":

                    value = c.recv(1024)
                    if (value != 'end'):
                        board[place // 3][place % 3] = value
                    place += 1
                    print("array: ", value)
                return board


            sleep(0.5)

    except KeyboardInterrupt:
        sys.exit(1)

# Pelaajan vuoro alkaa
def PlayerTurn(s, c):
    print("playerturn")
    msg = "asd"
    try:
        while msg != "oke":
            c.send("player_turn")
            sleep(0.1)
            msg = c.recv(1024)

    except KeyboardInterrupt:
        sys.exit(1)


# Siirtää robotin nappulan valintanappulan pois ruudulta
def RemoveStartingMark(s, c):
    print("remove")
    msg = "asd"
    try:
        while msg != "oke":
            c.send("gameover")
            sleep(0.1)
            msg = c.recv(1024)
            print(msg)

    except KeyboardInterrupt:
        sys.exit(1)

# Vastaanottaa robotin näkemän starttinappulan
def ReceiveStartingMark(s, c):
    print("receive")
    msg = "asd"
    try:
        while msg != "1" and msg != "0":
            c.send("send_starter")
            sleep(0.1)
            msg = c.recv(1024)
            print(msg)
        print("startteri nappula: ", msg)
        return int(msg)

    except KeyboardInterrupt:
        sys.exit(1)

# kutsunta MarkCell(i*3+j, player)
# Ilmottaa robotille minne laitetaan nappula, ja mikä nappula
def MarkCell(position, player, s, c):
    global coordinates
    print("sortattu", coordinates)
    try:
        msg = "asd"
        while msg != "oke":

            sleep(0.1)
            count = 0
            c.send("mark_cell")
            msg = c.recv(1024)
            print(msg)

        while(True): #count < 10
            # Ilmoitetaan robotille, haluttu nappulan sijainti
            msg = c.recv(1024)
            if msg == "ready_for_data":
                sleep(0.3)

                string = "({},{},{})"
                c.send(string.format(coordinates[position][0], coordinates[position][1], position) )
                print("positio viesti", string.format(coordinates[position][0], coordinates[position][1], position))

                return

            sleep(0.5)

        print("meni muka pois")
    except KeyboardInterrupt:
        sys.exit(1)


# Yhdistää robottiin
def Connect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #http://<robot_ip_address>:4242/current.jpg?annotations=<on|off>

        s.bind((HOST, PORT)) # Bind to the port
        s.listen(5) # Now wait for client connection.
        c, addr = s.accept() # Establish connection with client.
        return s, c, addr
    except KeyboardInterrupt:
        sys.exit(1)

