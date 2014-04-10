#!/usr/bin/python

#Kevin Langer
# A1 - CS4100
# Ticktacktoe

import sys 
import random
import collections
import re

# Board is represented as a simple array
# Populated with 2 for a player 
# Populated with 4 for NPC 
# Not populated with 3 (but indicates draw)
# 2 and 4 picked because 2&bitwise4=0
board = [
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
]
# Player 1 and 2 are human and computer
# Note they do alternate but keep their X or O
players = ["-","Human(X)","Computer(O)"]
global turn
turn = 0
def spec_check_board(spec_board): 
    if (spec_board[0] & spec_board[4] & spec_board[8]):
        return spec_board[0]
    if (spec_board[2] & spec_board[4] & spec_board[6]):
        return spec_board[2]
    corner_places = [0,2,6,8]
    for x in xrange(3):
        #Check vertical for win
        if spec_board[x] & spec_board[x+3] & spec_board[x+6]:
            return spec_board[x]
        #Check horizontal
        if spec_board[x*3] & spec_board[x*3+1] & spec_board[x*3+2]:
            return spec_board[x*3]
    return 3 #draw if game is over
def check_board():
    winner = spec_check_board(board)
    if (winner!=3):
        print "Player %s Wins!" % players[winner/2]
        return winner
def draw_board():
    count = 0
    #Replace numbers with symbols for player engagement
    XO = "-","-","X","-","O"
    print "  1 2 3"
    for spaces in board:
        if (count % 3 == 0):
            print count/3 + 1,
        print XO[spaces], 
        count = count + 1
        if count % 3 == 0:
            print ""
def update_board(index,player):
    #Report who wins, use global player array
    print "Player %s's turn" % players[player/2]
    global turn
    turn = turn + 1  
    board[index] = player

def player_position():
    print "Enter input (1-3) 'x' <space> 'y':"
    while 1:
        line = sys.stdin.readline()
        # Only accept 1-3
        is_match = re.match(r"([1-3])[\s\t,]+([1-3])",line)
        if (is_match):
            #Regex allows for a tab, space, or comma when entering
            i = int(is_match.group(1))-1+3*(int(is_match.group(2))-1)
        else:
            print "Invalid input: not even a correct index\n \
                redrawing the board for refrence"
            draw_board()
            print "Please try again: "
            continue
        if i > 8 or i < 0 or board[i]:
            print "Invalid input: Space already taken or out of bounds\n \
                redrawing board for refrence"
            draw_board()    
            print "Please try again: "
            continue
        return i
def get_boards(board_t, player):
    boards = []
    #Create all boards possible for the next turn
    # boards will be an array of board sized 0-9
    for x in xrange(9):
        if (board_t[x] == 0):
            boardCpy = board_t[:]
            boardCpy[x] = player
            boards.append(boardCpy)
    return boards   
def next_player(player):
    # Cycle players
    if (player == 2): 
        return 4
    return 2
def minimax(board_t, player):
    variation = []
    winner = spec_check_board(board_t) 
    #No need to depth limit tick tack toe
    # only 9!
    if (winner != 3):
        return (winner,board_t)
    boards = get_boards(board_t,player)
    local_score = next_player(player)
    # If there are no game boards, it is clearly already draw
    if (len(boards) == 0):
        return (3,board_t)
    # Calculate minimax for all boards
    for x in range(len(boards)):
        #Work down sub-boards to calcualte minimax for all branches
        (winner,board_) = minimax(boards[x],next_player(player)) 
        # Note, for maximizing player the score is 4 for win
        # 3 for draw and 2 for loss. I used 4 and 2 for team #s so 
        # I could use bitwise and. 
        if (player == 4): #max
            if ( winner > local_score):
                # Not only save who will win, but also save the 
                # trace of moves to get to the win
                local_score = winner
                variation.append(boards[x])
        else: #min
            local_score = min(local_score,winner)
    # return the tuple of winner and the trace of moves
    return (local_score,variation)  
def diff(board1,board2):
    # Because I return a board instead of a move 
    # I need to know what actually changes
    for x in xrange(9):
        if (board1[x] != board2[x]):
            return x
def hueristic():
    # The first move would take a while
    # But the computer always picked top left
    # I know that picking the corners for the first 
    # or second move will never result in a loss
    # so this results in a more interesting computer
    while True:
        places = [0,2,6,8]
        i = random.randrange(0,4)
        if not board[places[i]]:
            return places[i]
def computer_position(player):
    # To reduce runtime and make computer more
    # human-like
    if (turn < 1):
        return hueristic() 
    # throw away whoCanWin (spoilers its always the computer
    # or nobody)
    (whoCanWin,move) = minimax(board,player)
    return diff(move.pop(),board)
def draw(t):
    if t == 9:
        print "Draw"
        draw_board()
        return 1
    return 0
# was used for testing#
#def random_position():
#    while True:
#        i = random.randrange(0,9)
#        if not board[i]:
#            return i
def choose_starting_player(): 
    comp = random.randrange(0,2)
    #assert(comp == 0 or comp == 1)
    print "%s goes first!" % players[comp+1]
    return comp
def main():
    compFirst = choose_starting_player()
    while True:
        if compFirst:
            player_1 = computer_position(4)
            update_board(player_1,4)
        else:
            player_1 = player_position()
            #player_1 = random_position()
            update_board(player_1,2)
        draw_board()
        if check_board() or draw(turn):
            break
        if not compFirst:
            player_2 = computer_position(4)
            update_board(player_2,4)
        else:
            player_2 = player_position()
            #player_2 = random_position()
            update_board(player_2,2)
        draw_board()
        if check_board() or draw(turn):
            break
if __name__ == "__main__":
    main()
