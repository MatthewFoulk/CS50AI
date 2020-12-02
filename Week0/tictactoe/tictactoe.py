"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
NUM_TO_WIN = 3
MIN = -1
MAX = 1


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board. 
    X-player always moves first.
    """
    xCount = 0 # Appearances of X on the board
    oCount = 0 # Apprearances of O on the board

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == X:
                xCount+=1
            elif board[row][col] == O:
                oCount+=1
    
    return O if oCount < xCount else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                actions.add((row, col))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row = action[0]
    col = action[1]
    if board[row][col] != EMPTY:
        raise Exception

    playerTurn = player(board)
    boardCopy = copy.deepcopy(board)
    boardCopy[row][col] = playerTurn
    return boardCopy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    winInRow = checkWinInRow(board)
    if winInRow != None:
        return winInRow
    
    winInCol = checkWinInCol(board)
    if winInCol != None:
        return winInCol
    
    winInDiag = checkWinInDiag(board)
    if winInDiag != None:
        return winInDiag
    
    return None

def checkWinInRow(board):
    """
    Determine if a player has won on the current board from any of
    the three rows
    """
    for row in range(len(board)):
        currPlayer = board[row][0];
        count = 0
        if currPlayer == EMPTY:
            continue
        for col in range(len(board[row])):
            if board[row][col] == currPlayer:
                count+=1
        
        if count == NUM_TO_WIN:
            return currPlayer
    return None
            
def checkWinInCol(board):
    """
    Determine if a player has won on the current board from any of 
    the three columns
    """
    for col in range(len(board[0])):
        currPlayer = board[0][col];
        count = 0
        if currPlayer == EMPTY:
            continue
        for row in range(len(board)):
            if board[row][col] == currPlayer:
                count+=1

        if count == NUM_TO_WIN:
            return currPlayer
    return None

def checkWinInDiag(board):
    """
    Determine if a player has won on the current board from either
    of the two diagonals
    """
    # Check middle point
    middlePlayer = board[1][1]
    if middlePlayer == EMPTY:
        return None
    
    # Check left to right diagonal
    if board[0][0] == middlePlayer:
        if board[2][2] == middlePlayer:
            return middlePlayer
    
    # Check right to left diagonal
    if board[2][0] == middlePlayer:
        if board[0][2] == middlePlayer:
            return middlePlayer
    
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None or len(actions(board)) == 0:
        return True
    else: 
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winPlayer = winner(board)

    if winPlayer == X:
        return 1
    elif winPlayer == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        # Game is finished
        return None 

    playerTurn = player(board) # Determine who's turn it is

    if playerTurn == X:
        # Simulate X's turn
        maxMoveValue = -math.inf
        for action in actions(board):
            utility = minValue(result(board, action))
            if utility > maxMoveValue:
                # Updates the current best (max) move
                maxMoveValue = utility;
                maxMove = action
        return maxMove
    elif playerTurn == O:
        # Simulate O's turn
        minMoveValue = math.inf
        for action in actions(board):
            utility = maxValue(result(board, action))
            if utility < minMoveValue:
                # Updates the current best (min) move
                minMoveValue = utility
                minMove = action
        return minMove


def maxValue(board):
    """ 
    Recursively calls the minValue function until the max is found
    or all actions have been exhausted. Returns the maximum/optimal
    outcome found from remaining actions.
    """
    maxValue = -math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        maxValue = max(maxValue, minValue(result(board, action)))
        if maxValue == MAX:
            # Stops the search short because the max has already
            # been found
            return maxValue
    return maxValue

def minValue(board):
    """ 
    Recursively calls the maxValue function until the min is found
    or all actions have been exhausted. Returns the minimum/optimal
    outcome found from remaining actions.
    """
    minValue = math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        minValue = min(minValue, maxValue(result(board,action)))
        if minValue == MIN:
            # Stops the search short because the min has already
            # been found
            return minValue
    return minValue