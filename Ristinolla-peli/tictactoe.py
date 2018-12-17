#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
import random
import ai
import robosocket
import os

from time import sleep
import requests
import urllib

lastCell = 999

# Peli alustan luonti
def createBoard():
    return(np.array([[0, 0, 0],
                     [0, 0, 0],
                     [0, 0, 0]]))

 # Summittaisen paikan valitseminen
def randomPlace(board, player):
    selection = ai.possibilities(board)
    print(ai.possibilities(board))
    current_loc = random.choice(selection)
    board[current_loc] = player
    return(board)

def drawBoard(board):
    #os.system('cls')
    count = 0
    rows = board.shape[0]
    cols = board.shape[1]
    print ("\n-------------")

    for x in range(rows):
        print ("|", end ='')
        for y in range(cols):
            count += 1
            if (board[x][y] == 0):
                if (count <= 9):
                    print ("", end =' ')
                #print (count, end =' ')
                print ("-", end =' ')
            elif board[x][y] == 1:
                print (" O", end =' ')
            elif board[x][y] == 2:
                print (" X", end =' ')
            print ("|", end ='')
        print ("\n-------------")


# Pelaajan paikan valitseminen, kun pelaaja pelaa komentorivillä
def getPlayerPlace(board, player, s, c):
    print("Pelaajan vuoro\n")
    rows = board.shape[0]
    cols = board.shape[1]

    while True:
        temp = -1
        place = input() - 1
        if place >= 0 and place < 9:
            temp = board[place // cols][place % cols]

        if temp == 0:
            board[place // cols][place % cols] = player
            winner = ai.checkWinner(board, player)

            return board, winner
        else:
            print ("Invalid movement")

# Lähettää kuvan pelitilanteesta kotisivulle
def sendImage():
    picUrl = 'http://192.168.100.10:4242/current.jpg?type=color'

    with open('ristinolla.jpg', 'wb') as handle:
        response = requests.get(picUrl, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

    url = 'http://www.students.oamk.fi/~t6jaje00/post.php'

    resp = urllib.urlopen(picUrl)

    files = {'file': open('ristinolla.jpg', 'rb')}

    r = requests.post(url, files=files)

def playGame(s, c):
    board, winner, counter = createBoard(), 0, 1
    lastmoves = []
    drawBoard(board)

    #print(board)
    while winner == 0:
        player = 1

        if robotStartsGame == True:
            print("vaihtoehto 1")
            sleep(5)
            board, winner = ai.robotMove(board, player, counter, s, c)
            sendImage()
        else:
            print("vaihtoehto 2")
            robosocket.PlayerTurn(s, c)
            board = robosocket.ReceiveBoard(s, c)
            winner = ai.checkWinner(board, player)
            sendImage()

        drawBoard(board)

        counter += 1
        if winner != 0:
            break


        player = 2

        if robotStartsGame == False:
            print("vaihtoehto 4")
            board, winner = ai.robotMove(board, player, counter, s, c)
            sendImage()
        else:
            print("vaihtoehto 3")
            robosocket.PlayerTurn(s, c)
            board = robosocket.ReceiveBoard(s, c)
            winner = ai.checkWinner(board, player)
            sendImage()




        #board, winner = ai.robotMove(board, player, counter, s, c)

        drawBoard(board)

        counter += 1

        if winner != 0:
            break

    return(winner)


# Aloitus koodi
print("Peli alkaa, pyydetään koordinaatit robotilta")
s, c, addr = robosocket.Connect() # yhteys päälle
robosocket.GetCoordinates(s, c)
isFirstGame = True
robotStartsGame = False

while True:
    if isFirstGame == False:
        # Muilla kuin ensimmäisellä pelikerralla, aluksi siirretään robotin valintanappula pois ruudukolta
        robosocket.RemoveStartingMark(s, c)

    isFirstGame = False # Seuraava pelikerta ei ole enää ensimmäinen
    # Robotti aloittaa pelin tai pelaaja aloittaa
    robotStartsGame = robosocket.ReceiveStartingMark(s, c)

    winner = playGame(s, c)
    if (winner == -1):
        print("Tasapeli")
    elif (winner == 1):
        print("O vei")
    elif (winner == 2):
        print("X vei")





