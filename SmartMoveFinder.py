import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 10000
STALEMATE = 0
DEPTH = 3

'''
Computer does a random move from list of validMoves
'''


def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]  # returns number between a and b


def find_best_move(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentsMoves = gs.get_valid_moves()
        opponentsMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.make_move(opponentsMove)
            gs.get_valid_moves()
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * score_material(gs.board)
            if score > opponentsMaxScore:
                opponentsMaxScore = score
            gs.undo_move()
        if opponentsMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentsMaxScore
            bestPlayerMove = playerMove
        gs.undo_move()
    return bestPlayerMove


'''
Finds best move using min-max algorithm
'''


def find_best_move_min_max(gs, validMoves):
    global counter
    counter = 0
    turnScalar = 1 if gs.whiteToMove else -1  # This will scale move calculation according to player's turn
    bestMoves = min_max(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, turnScalar)  # List of equally best moves if
    # there are multiple
    randomInt = random.randint(0, len(bestMoves) - 1)
    print("counter = " + str(counter))
    return bestMoves[randomInt]


'''
min-max algorithm for calculating best moves
'''


def min_max(gs, validMoves, depth, alpha, beta, turnScalar):  # Implementing alpha-beta pruning
    global counter
    counter += 1
    if depth == 0:
        return score_board(gs)

    bestMoves = []
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.get_valid_moves()
        score = -min_max(gs, nextMoves, depth - 1, -beta, -alpha, -turnScalar)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMoves = [move]  # If there is new higher value, replace list with new best move
        elif score == maxScore:
            if depth == DEPTH:
                bestMoves.append(move)
        gs.undo_move()
        if maxScore > alpha:  # Pruning
            alpha = maxScore
        if alpha >= beta:
            break
    if depth == DEPTH:
        return bestMoves
    else:
        return maxScore


'''
Score Board
'''


def score_board(gs):
    print("gs.checkmate " + str(gs.checkmate))
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for rank in gs.board:
        for square in rank:
            pieceColor = square[0]
            piece = square[1]
            if pieceColor == 'w':
                score += pieceScore[piece]
            elif pieceColor == 'b':
                score -= pieceScore[piece]
    return score


'''
Finds the score based on material
'''


def score_material(board):
    score = 0
    for rank in board:
        for square in rank:
            pieceColor = square[0]
            piece = square[1]
            if pieceColor == 'w':
                score += pieceScore[piece]
            elif pieceColor == 'b':
                score -= pieceScore[piece]
    return score

# pawn = 1
# bishop = 3
# knight = 3
# rook = 5
# queen = 9
# king = 1000
