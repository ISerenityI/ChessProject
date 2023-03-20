import random

pieceScore = {"K": 1000, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 10000
STALEMATE = 0


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
