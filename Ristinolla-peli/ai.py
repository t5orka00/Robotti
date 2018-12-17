#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import time
import robosocket

# Tarkistaa tyhjät ruudut pelialustalla
def possibilities(board):
    l = []

    for i in range(len(board)):
        for j in range(len(board)):

            if board[i][j] == 0:
                l.append((i, j))
    return(l)


# Vaaka voitto
def rowWin(board, player):
    for x in range(len(board)):
        win = True

        for y in range(len(board)):
            if board[x, y] != player:
                win = False
                continue

        if win == True:
            return(win)
    return(win)


# Pysty voitto
def colWin(board, player):
    for x in range(len(board)):
        win = True

        for y in range(len(board)):
            if board[y][x] != player:
                win = False
                continue

        if win == True:
            return(win)
    return(win)


# Vino voitto
def diagWin(board, player):
    win = True
    for x in range(len(board)):
        if ((board[x, x] != player) and (board[2, 0] != player or board[1, 1] != player or board[0, 2] != player)):
            win = False

    return(win)

# palauttaa voittajan numeron tai -1 jos tasapeli, 0 jos pelialue ei täynnä ja ei voittajaa vielä'
def checkWinner(board, player):
    winner = 0

    if (rowWin(board, player) or
        colWin(board,player) or
        diagWin(board,player)):
        winner = player

    if np.all(board != 0) and winner == 0: # pelialue täynnä, ei voittajaa = tasapeli
        winner = -1
    return winner

# Simulointia varten merkkaa ruutuun oman nappulan
def mark(board, player, pos, lastmoves):
    board[pos] = player
    lastmoves.append(pos)
    return(board, lastmoves)


# Ottaa viimeisimmän simuloidun nappulan pois ruudulta
def removeLastMove(board, lastmoves):
    board[lastmoves.pop()] = '0'
    winner = None
    return board, lastmoves


# Robotin vuoron toteutus
def robotMove(board, player, counter, s, c):
    l = []
    print("Robotin vuoro\n")
    start = time.clock()
    sscore,movePosition,score = maximizedMove(board, player, l, -999, 999, 9, counter) # Aloittaa rekursiivisen minmax algoritmin

    end = time.clock()
    print("Aikaa robotin vuoroon kului: ", end - start)

    board, lastmoves = mark(board, player, movePosition, l)

    robosocket.MarkCell(movePosition[0]*3 + movePosition[1], player, s, c)
    print("suunta:", movePosition[0]*3 + movePosition[1])

    winner = checkWinner(board, player)
    return board, winner


def maximizedMove(board, me, lastmoves, alpha, beta, syvyys, counter):
    # simuloitu oma paras mahdollinen siirto

    # #### Pisteiden lasku #####
    # Siirto valitaan suurimman saadun pistemäärän perusteella.
    # Robotin voittava siirto

    sscore = 0
    bestScore = -999
    bestscore = None
    bestmove = None
    score = 0

    # board = nykyinen pelitilanne + simuloidut siirrot algoritmia varten
    # m = pos = haluttu sijainti muodossa 1 2 3 4   halutaan muuttaa muotoon [0,0] ... [2,2]
    # lastmoves = viimesimmät simuloidut siirrot

    for m in possibilities(board):
        board, lastmoves = mark(board, me, m, lastmoves)   # board, player, pos, lastmoves

        if (counter >= 5):
            winner = checkWinner(board, me) # 0 ei voittoa, 1 pelaaja 1 voitti, 2 pelaaja 2 voitti
            if (winner == me):
                sscore = syvyys
            elif (winner == -1): # tasapeli
                sscore = 0
            else:
                sscore,movePosition,score = minimizedMove(board, me, lastmoves, alpha, beta, syvyys-1, counter+1)
        else:
            sscore,movePosition,score = minimizedMove(board, me, lastmoves, alpha, beta, syvyys-1, counter+1)

        bestScore = max(bestScore, sscore)

        if bestScore > alpha:
            alpha = bestScore
            bestmove = m


        board, lastmoves = removeLastMove(board, lastmoves)

        if beta <= alpha:
            break

    return bestScore, bestmove, bestscore

def minimizedMove(board, me, lastmoves, alpha, beta, syvyys, counter):
    # simuloitu vastustajan paras mahdollinen siirto
    sscore = 0
    bestScore = 999
    bestscore = None
    bestmove = None
    score = 0

    if me == 1:
        opponent = 2
    else:
        opponent = 1

    for m in possibilities(board):

        board, lastmoves = mark(board, opponent, m, lastmoves)   # board, player, pos, lastmoves
        if (counter >= 5):
            winner = checkWinner(board, opponent) # 0 ei voittoa, 1 pelaaja 1 voitti, 2 pelaaja 2 voitti
            if (winner == opponent):
                sscore = -syvyys
            elif (winner == -1): # oletettavasti tasapeli
                sscore = 0
            else:
                sscore, movePosition,score = maximizedMove(board, me, lastmoves, alpha, beta, syvyys-1, counter+1)
        else:
            sscore, movePosition,score = maximizedMove(board, me, lastmoves, alpha, beta, syvyys-1, counter+1)

        bestScore = min(bestScore, sscore)

        if bestScore < beta:
            beta = bestScore
            bestmove = m

        board, lastmoves = removeLastMove(board, lastmoves)
        #Jos maximized pistemäärä > minimizedista

        if beta <= alpha:
            break

    return bestScore, bestmove, bestscore
