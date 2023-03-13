"""This is ChessMain driver file. It will be responsible for displaying the current state of the game and handling in
user input."""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 720
DIMENSION = 8  # Chess Board has dimensions 8x8.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''


def load_images():
    pieces = ["wK", "wQ", "wR", "wB", "wN", "wP", "bK", "bQ", "bR", "bB", "bN", "bP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("ChessImages\\" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note that we can now use the images we load, i.e. IMAGES["wK"]


'''
The main driver for our code. This will handle user input and render the graphics.
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.game_state()
    validMoves = gs.get_valid_moves()
    moveMade = False  # Flag variable for when a move is made
    animate = False  # Flag variable for when we should animate
    load_images()  # Only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is selected initially. Keeps track of user's last click (tuple: (# rank, file))
    player_clicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    file = location[0] // SQ_SIZE
                    rank = location[1] // SQ_SIZE
                    if sqSelected == (rank, file):  # The user clicked the same square twice
                        sqSelected = ()  # deselect
                        player_clicks = []  # Clear player clicks
                    else:
                        sqSelected = (rank, file)
                        player_clicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    if len(player_clicks) == 2:  # after the 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        if move in validMoves:
                            pawnPromotion = (move.pieceMoved[1] == 'P') and (move.endRank == 7 or move.endRank == 0)
                            if pawnPromotion:
                                allyColor = move.pieceMoved[0]
                                promotionPieces = [allyColor + 'Q', allyColor + 'R', allyColor + 'B', allyColor + 'N']
                                result = pawn_promotion(move, screen)
                                if not result:
                                    running = False
                                elif result in promotionPieces:
                                    gs.promotePawn = result
                                    gs.make_move(move)
                                    moveMade = True
                                    sqSelected = ()
                                    player_clicks = []
                                elif result == ():
                                    sqSelected = result
                                    player_clicks = []
                                else:
                                    player_clicks = result
                            else:
                                gs.make_move(move)
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                player_clicks = []
                        else:
                            player_clicks = [sqSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:  # undo move when 'u' is pressed
                    gs.undo_move()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = ChessEngine.game_state()
                    validMoves = gs.get_valid_moves()
                    sqSelected = ()
                    player_clicks = []
                    moveMade = False
                    animate = False
        if moveMade:
            if animate:
                animate_move(screen, gs.moveLog[-1], gs.board, clock)
            validMoves = gs.get_valid_moves()
            moveMade = False

        draw_game_state(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


'''
This will prompt a pawn promotion bar if the player wishes to promote
'''


def pawn_promotion(move, screen):
    promotionRank = move.endRank
    promotionFile = move.endFile
    pieceColor = move.pieceMoved[0]
    promotionPieces = [pieceColor + 'Q', pieceColor + 'R', pieceColor + 'B', pieceColor + 'N']
    color = p.Color("light grey")
    selectPiece = {}
    selectSQ = []
    if promotionRank == 0:
        for r in range(4):
            rank = r
            file = promotionFile
            piece = promotionPieces[r]
            p.draw.rect(screen, color, p.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            screen.blit(IMAGES[piece], p.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            selectPiece[(rank, file)] = piece
            selectSQ.append((rank, file))
        p.draw.rect(screen, color, p.Rect(promotionFile * SQ_SIZE, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE // 2))
        p.display.flip()
        while True:
            for e in p.event.get():
                if e.type == p.QUIT:  # In case user wants to close application during pawn promotion
                    return False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    file = location[0] // SQ_SIZE
                    halfRank = location[1] // (SQ_SIZE // 2)
                    rank = halfRank // 2
                    selectedPiece = (rank, file) in selectSQ
                    if selectedPiece:
                        return selectPiece[(rank, file)]
                    elif (halfRank, file) == (7, promotionFile):
                        return ()
                    else:
                        return [(rank, file)]
    else:
        for r in range(4):
            rank = 7 - r
            file = promotionFile
            piece = promotionPieces[r]
            p.draw.rect(screen, color, p.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            screen.blit(IMAGES[piece], p.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            selectPiece[(rank, file)] = piece
            selectSQ.append((rank, file))
        p.draw.rect(screen, color, p.Rect(promotionFile * SQ_SIZE, (3 * SQ_SIZE) + SQ_SIZE // 2, SQ_SIZE, SQ_SIZE // 2))
        p.display.flip()
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:  # In case user wants to close application during pawn promotion
                return False
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of mouse
                file = location[0] // SQ_SIZE
                halfRank = location[1] // (SQ_SIZE // 2)
                rank = halfRank // 2
                selectedPiece = (rank, file) in selectSQ
                if selectedPiece:
                    return selectPiece[(rank, file)]
                elif (halfRank, file) == (9, promotionFile):
                    return ()
                else:
                    return [(rank, file)]


'''
Highlight the square selected and moves a piece can make
'''


def highlight_squares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRank == r and move.startFile == c:
                    screen.blit(s, (move.endFile * SQ_SIZE, move.endRank * SQ_SIZE))


'''
Responsible for all the graphics in its current game state.
'''


def draw_game_state(screen, gs, validMoves, sqSelected):
    draw_board(screen)  # draw the squares on the board
    highlight_squares(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, gs.board)  # draw pieces on to top of the squares they are.


'''
Draw the board. The top left square is always a light color.
'''


def draw_board(screen):
    colors = [p.Color("white"), p.Color("orange")]
    for r in range(DIMENSION):
        for f in range(DIMENSION):
            color = colors[((r + f) % 2)]
            p.draw.rect(screen, color, p.Rect(f * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board
'''


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for f in range(DIMENSION):
            piece = board[r][f]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(f * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Animating move
'''


def animate_move(screen, move, board, clock):
    colors = [p.Color("white"), p.Color("orange")]
    dR = move.endRank - move.startRank
    dF = move.endFile - move.startFile
    framesPerSquare = 10  # Frames to move one square
    frameCount = (abs(dR) + abs(dF)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRank + dR * frame / frameCount, move.startFile + dF * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        # Erase the piece moved from it's ending square
        color = colors[(move.endRank + move.endFile) % 2]
        endSquare = p.Rect(move.endFile * SQ_SIZE, move.endRank * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceMoved], endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


'''
Writes text on the board
'''


def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2,
                                                    HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
