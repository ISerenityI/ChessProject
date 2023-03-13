"""This module is responsible for storing all the information about the current state of the game. It will also be
responsible for determining legal moves at the current state. In addition, it will log all moves."""


class game_state:
    def __init__(self):
        # Board is a 8x8 2D list. Each element in the list has 2 characters. First character represents the color of
        # the piece. w for white and b for black. The second character represents the type of piece: Q (Queen),
        # K (King), R (Rook), B (Bishop), N (Knight) and P (Pawn). The string "--" represents an empty space.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'K': self.get_king_moves, 'Q': self.get_queen_moves, 'R': self.get_rook_moves,
                              'B': self.get_bishop_moves, 'N': self.get_knight_moves, 'P': self.get_pawn_moves}
        self.whiteToMove = True
        self.moveLog = []
        # The following keeps track of the locations for every piece except the knight and pawns. This will be useful
        # when checking for pins
        self.pieceLocation = {'wK': (7, 4), 'wQ': [(7, 3)], 'wB': [(7, 2), (7, 5)],
                              'wR': [(7, 0), (7, 7)], 'bK': (0, 4), 'bQ': [(0, 3)],
                              'bB': [(0, 2), (0, 5)], 'bR': [(0, 0), (0, 7)]}
        self.pins = []  # Will store square that is pinned and direction of pin
        self.checkMate = False
        self.staleMate = False

        self.promotePawn = ''  # If pawn is promoted, this will hold information regarding promotion piece

        self.enPassantMoves = []  # Logs move instances where en passant can occur

        # The following attributes keeps track of player's castling rights. Will track if player may castle king side
        # (short) or queen side (long)
        self.castlingRights = {'w': (True, True), 'b': (True, True)}  # (short, long)
        self.canCastle = (False, False)  # Checks if player can castle. (short, long)
        self.castleMoves = []  # Logs move instances where castling can occur

    '''
    Takes a move as a parameter and executes it 
    '''

    def make_move(self, move):
        if self.whiteToMove:
            playerColor = 'w'
            enemyColor = 'b'
        else:
            playerColor = 'b'
            enemyColor = 'w'
        self.whiteToMove = not self.whiteToMove  # Switch turns
        self.board[move.startRank][move.startFile] = "--"
        self.board[move.endRank][move.endFile] = move.pieceMoved
        pieceNeedUpdate = ['wK', 'wQ', 'wB', 'wR', 'bK', 'bQ', 'bB', 'bR']  # Piece's that need to update location

        # Check if move causes enemy to lose castling rights (short or long). If enemy rook is captured, then opponent
        # loses rights to castle on the same side
        enemyCastlingRights = self.castlingRights[enemyColor][0] or self.castlingRights[enemyColor][1]
        if enemyCastlingRights:
            if move.pieceCaptured == enemyColor + 'R':
                if move.endFile == 7:
                    self.castlingRights[enemyColor] = (False, self.castlingRights[playerColor][1])
                else:
                    self.castlingRights[enemyColor] = (self.castlingRights[playerColor][0], False)

        if move in self.castleMoves:  # This executes castling
            for m in self.castleMoves:
                if move == m:
                    rookStartRank, rookStartFile = m.castle[0]
                    rookEndRank, rookEndFile = m.castle[1]
                    self.board[rookStartRank][rookStartFile] = "--"
                    self.board[rookEndRank][rookEndFile] = playerColor + "R"
                    for i in range(len(self.pieceLocation[playerColor + "R"])):  # Update rook location
                        if (rookStartRank, rookStartFile) == self.pieceLocation[playerColor + "R"][i]:
                            self.pieceLocation[playerColor + "R"][i] = (rookEndRank, rookEndFile)
                            break
                    self.pieceLocation[move.pieceMoved] = (move.endRank, move.endFile)  # Update king location
                    m.castlingRights = self.castlingRights[playerColor]  # Preserves castling rights
                    self.moveLog.append(m)
                    break
            self.castlingRights[playerColor] = (False, False)  # Once castled no more castling rights
        elif move in self.enPassantMoves:  # This executes en passant
            for m in self.enPassantMoves:
                if move == m:
                    r, f = m.enPassant
                    self.board[r][f] = "--"
                    self.moveLog.append(m)
                    break
        # If the move is promoting a pawn, this conditional will promote the pawn
        elif self.promotePawn != '':
            self.board[move.endRank][move.endFile] = self.promotePawn
            if self.promotePawn in pieceNeedUpdate:
                self.pieceLocation[self.promotePawn].append((move.endRank, move.endFile))
            self.promotePawn = ''
            self.moveLog.append(move)
        else:
            # This will update castling rights if either a rook or king is moved for the first time
            castlingRights = self.castlingRights[playerColor][0] or self.castlingRights[playerColor][1]
            if castlingRights:
                if move.pieceMoved == playerColor + 'K':
                    move.castlingRights = self.castlingRights[playerColor]
                    self.castlingRights[playerColor] = (False, False)
                elif move.pieceMoved == playerColor + 'R':
                    if move.startFile == 7:
                        move.castlingRights = self.castlingRights[playerColor]
                        self.castlingRights[playerColor] = (False, self.castlingRights[playerColor][1])
                    else:
                        move.castlingRights = self.castlingRights[playerColor]
                        self.castlingRights[playerColor] = (self.castlingRights[playerColor][0], False)

            # Update the piece location if moved for queen, king, bishop or rook
            if move.pieceCaptured in pieceNeedUpdate:
                for j in self.pieceLocation[move.pieceCaptured]:
                    if (move.endRank, move.endFile) == j:
                        self.pieceLocation[move.pieceCaptured].remove(j)
                        break
            if move.pieceMoved in pieceNeedUpdate:
                if type(self.pieceLocation[move.pieceMoved]) == list:
                    for i in range(len(self.pieceLocation[move.pieceMoved])):
                        if (move.startRank, move.startFile) == self.pieceLocation[move.pieceMoved][i]:
                            self.pieceLocation[move.pieceMoved][i] = (move.endRank, move.endFile)
                            break
                else:
                    self.pieceLocation[move.pieceMoved] = (move.endRank, move.endFile)
            self.moveLog.append(move)  # Log the move so we can undo it later

        # Reset attributes that do not need to be carried over to the next turn. This will prevent bugs that might
        # occur if attributes are not reset
        self.castleMoves = []
        self.enPassantMoves = []
        self.canCastle = (False, False)
        self.promotePawn = ''

    '''
    Undo the last move
    '''

    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            self.whiteToMove = not self.whiteToMove  # Switch turns
            if self.whiteToMove:
                playerColor = 'w'
                enemyColor = 'b'
            else:
                playerColor = 'b'
                enemyColor = 'w'
            move = self.moveLog.pop()
            pieceNeedUpdate = ['wK', 'wQ', 'wB', 'wR', 'bK', 'bQ', 'bB', 'bR']  # Piece's that need to update locations

            if move.castle:
                self.castlingRights[playerColor] = move.castlingRights
                self.board[move.startRank][move.startFile] = move.pieceMoved
                self.board[move.endRank][move.endFile] = move.pieceCaptured
                rookStartRank, rookStartFile = move.castle[0]
                rookEndRank, rookEndFile = move.castle[1]
                self.board[rookStartRank][rookStartFile] = playerColor + 'R'
                self.board[rookEndRank][rookEndFile] = "--"
                for i in range(len(self.pieceLocation[playerColor + "R"])):  # Update rook location
                    if (rookEndRank, rookEndFile) == self.pieceLocation[playerColor + "R"][i]:
                        self.pieceLocation[playerColor + "R"][i] = (rookStartRank, rookStartFile)
                        break
                self.pieceLocation[move.pieceMoved] = (move.startRank, move.startFile)  # Update king location
            elif move.enPassant:  # This undoes en passant move
                self.board[move.startRank][move.startFile] = move.pieceMoved
                self.board[move.endRank][move.endFile] = "--"
                r, f = move.enPassant
                self.board[r][f] = enemyColor + 'P'
            else:
                # Checks if move being undone affected castling rights. If so, revert castling rights attribute back
                if move.castlingRights:
                    self.castlingRights[playerColor] = move.castlingRights

                # Makes move
                self.board[move.startRank][move.startFile] = move.pieceMoved
                self.board[move.endRank][move.endFile] = move.pieceCaptured

                # Check if pieceLocation needs to be updated
                if move.pieceCaptured in pieceNeedUpdate:
                    self.pieceLocation[move.pieceCaptured].append((move.endRank, move.endFile))
                if move.pieceMoved in pieceNeedUpdate:  # Will undo location change for piece in pieceNeedUpdate
                    if type(self.pieceLocation[move.pieceMoved]) == list:
                        pieceLocations = self.pieceLocation[move.pieceMoved]
                        for i in range(len(pieceLocations)):
                            if (move.endRank, move.endFile) == pieceLocations[i]:
                                self.pieceLocation[move.pieceMoved][i] = (move.startRank, move.startFile)
                    else:
                        self.pieceLocation[move.pieceMoved] = (move.startRank, move.startFile)

    '''
    All moves without considering checks
    '''

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # number of ranks
            for f in range(len(self.board[r])):  # number of files in a rank
                turn = self.board[r][f][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][f][1]
                    self.moveFunctions[piece](r, f, moves)  # This will call the appropriate move function based on
                    # piece type
        return moves

    '''
    All moves considering checks. This is the first function called by the ChessMain module
    '''

    def get_valid_moves(self):
        moves = []
        if self.whiteToMove:
            allyColor = 'w'
            kingRank = self.pieceLocation['wK'][0]
            kingFile = self.pieceLocation['wK'][1]
            print("\nWhite's turn")
        else:
            allyColor = 'b'
            kingRank = self.pieceLocation['bK'][0]
            kingFile = self.pieceLocation['bK'][1]
            print("\nBlack's turn")

        print("Piece locations = " + str(self.pieceLocation))
        print("Castling right = " + str(self.castlingRights[allyColor]))

        # Following code checks if player can castle short (self.castlingRights[allyColor][0]) or long
        # (self.castlingRights[allyColor][1])
        castlingRights = self.castlingRights[allyColor][0] or self.castlingRights[allyColor][1]
        if castlingRights:
            possiblyShort = self.castlingRights[allyColor][0]
            possiblyLong = self.castlingRights[allyColor][1]
            for i in range(1, 3):
                inBetweenShort = self.board[kingRank][kingFile + i]
                underAttackShort = self.square_under_attack(kingRank, kingFile + i)
                inBetweenLong = self.board[kingRank][kingFile - i]
                underAttackLong = self.square_under_attack(kingRank, kingFile - i)
                if (inBetweenShort != "--" or underAttackShort != []) and possiblyShort:
                    possiblyShort = False
                if (inBetweenLong != "--" or underAttackLong != []) and possiblyLong:
                    possiblyLong = False
            self.canCastle = (possiblyShort, possiblyLong)

        # This loop will check for all pins and store them in a list called self.pins
        self.pins = self.in_pin()
        checks = self.square_under_attack(kingRank, kingFile)
        print("checks = " + str(checks))
        print("List of Piece locations pinned with direction = " + str(self.pins))
        # 2. For each move, make the move
        if checks:
            if len(checks) == 1:  # Only 1 check, so can block or move king
                moves = self.get_all_possible_moves()
                # To block a check simply move a piece into a square between enemy piece and king
                check = checks[0]  # Check information
                checkRank = check[0][0]
                checkFile = check[0][1]
                pieceChecking = self.board[checkRank][checkFile]  # Enemy piece causing the check
                validSquares = []  # Squares that pieces can move to
                # If knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRank, checkFile)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                            kingRank + check[1][0] * i,
                            kingFile + check[1][1] * i)  # check[1][0] and check[1][1] are the
                        # check directions
                        validSquares.append(validSquare)
                        # Once you get to piece end checks
                        if validSquare[0] == checkRank and validSquare[1] == checkFile:
                            break
                # Get rid of any moves that don't block check or move king.
                # When removing items from a list go backwards to prevent index errors
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # Move doesn't move king, so it must block or capture
                        if not (moves[i].endRank,
                                moves[i].endFile) in validSquares:  # Move doesn't block check or capture pieces
                            moves.remove(moves[i])
            else:  # Double check, king has to move
                self.get_king_moves(kingRank, kingFile, moves)
        else:  # Not in check so all moves are fine
            moves = self.get_all_possible_moves()

        if not moves:
            if checks:
                self.checkMate = True
            else:
                self.staleMate = True
        return moves

    '''
    Determine if an enemy piece pins an ally piece. Returns location of pin and direction
    '''

    def in_pin(self):
        pins = []
        possiblePin = ()  # Piece locations of possible pin
        if self.whiteToMove:
            allyColor = "w"
            kingRank = self.pieceLocation['wK'][0]
            kingFile = self.pieceLocation['wK'][1]
            bishopLocation = self.pieceLocation['bB']
            rookLocation = self.pieceLocation['bR']
            queenLocation = self.pieceLocation['bQ']
        else:
            allyColor = "b"
            kingRank = self.pieceLocation['bK'][0]
            kingFile = self.pieceLocation['bK'][1]
            bishopLocation = self.pieceLocation['wB']
            rookLocation = self.pieceLocation['wR']
            queenLocation = self.pieceLocation['wQ']
        for j in bishopLocation:  # Checks if there are any pins from enemy bishop
            r = j[0]
            f = j[1]
            if abs(kingRank - r) - abs(kingFile - f) == 0:
                distance = max(kingRank, r) - min(kingRank, r)
                # This is direction of bishop relative to king
                d = ((j[0] - kingRank) // distance,
                     (j[1] - kingFile) // distance)
                for i in range(1, distance):
                    rank = kingRank + d[0] * i
                    file = kingFile + d[1] * i
                    InBetween = self.board[rank][file]
                    if InBetween[0] == allyColor and possiblePin == ():
                        possiblePin = (rank, file)
                    elif InBetween != "--" and possiblePin != ():
                        possiblePin = ()
                        break
                if possiblePin != ():
                    pins.append([possiblePin, d])
        for j in rookLocation:  # Check if there is any pins from enemy rook
            r = j[0]
            f = j[1]
            if (r - kingRank == 0) or (f - kingFile == 0):
                distance = abs((r - kingRank) + (f - kingFile))
                d = ((r - kingRank) // distance,
                     (f - kingFile) // distance)  # This is direction of rook relative to king
                for i in range(1, distance):
                    rank = kingRank + d[0] * i
                    file = kingFile + d[1] * i
                    InBetween = self.board[rank][file]
                    if InBetween[0] == allyColor and possiblePin == ():
                        possiblePin = (rank, file)
                    elif InBetween != "--" and possiblePin != ():
                        possiblePin = ()
                        break
                if possiblePin != ():
                    pins.append([possiblePin, d])
        for j in queenLocation:
            r = j[0]
            f = j[1]
            # Checks if pin comes from diagonal
            fromDiagonal = abs(kingRank - r) - abs(kingFile - f) == 0
            fromRankFile = (r - kingRank == 0) or (f - kingFile == 0)
            if fromDiagonal:
                distance = max(kingRank, r) - min(kingRank, r)
                # This is direction of bishop relative to king
                d = ((j[0] - kingRank) // distance,
                     (j[1] - kingFile) // distance)
                for i in range(1, distance):
                    rank = kingRank + d[0] * i
                    file = kingFile + d[1] * i
                    InBetween = self.board[rank][file]
                    if InBetween[0] == allyColor and possiblePin == ():
                        possiblePin = (rank, file)
                    elif InBetween != "--" and possiblePin != ():
                        possiblePin = ()
                        break
                if possiblePin != ():
                    pins.append([possiblePin, d])
            elif fromRankFile:
                distance = abs((r - kingRank) + (f - kingFile))
                # This is direction of rook relative to king
                d = ((r - kingRank) // distance,
                     (f - kingFile) // distance)
                for i in range(1, distance):
                    rank = kingRank + d[0] * i
                    file = kingFile + d[1] * i
                    InBetween = self.board[rank][file]
                    if InBetween[0] == allyColor and possiblePin == ():
                        possiblePin = (rank, file)
                    elif InBetween != "--" and possiblePin != ():
                        possiblePin = ()
                        break
                if possiblePin != ():
                    pins.append([possiblePin, d])
        return pins

    '''
    All pieces attacking square (r, f). returns square location and direction of attack
    '''

    def square_under_attack(self, r, f):
        if self.whiteToMove:  # Check if black pieces attack squares
            enemyColor = 'b'
            allyColor = 'w'
            bishopLocation = self.pieceLocation['bB']
            rookLocation = self.pieceLocation['bR']
            queenLocation = self.pieceLocation['bQ']
            sq = []
        else:  # Check if white pieces attack square
            enemyColor = 'w'
            allyColor = 'b'
            bishopLocation = self.pieceLocation['wB']
            rookLocation = self.pieceLocation['wR']
            queenLocation = self.pieceLocation['wQ']
            sq = []

        # Check if Bishop is attacking
        for j in bishopLocation:
            onDiagonal = abs(j[0] - r) - abs(j[1] - f) == 0  # Checks if bishop is on same diagonal as square (r, f)
            if onDiagonal and j != (r, f):  # Piece on a square cannot attack same square
                distance = max(j[0], r) - min(j[1], r)
                # Bishop direction relative to square (r, f)
                d = ((j[0] - r) // abs(j[0] - r), (j[1] - f) // abs(j[1] - f))
                if distance == 1:
                    sq.append([j, d])
                else:
                    for i in range(1, 8):
                        rank = r + d[0] * i
                        file = f + d[1] * i
                        InBetween = self.board[rank][file]  # squares in between square (r, f) and Bishop
                        if (rank, file) != j:
                            # King cannot block squares under attack, since it will be in check. So, if the king is
                            # attacked, squares behind it can potentially be vulnerable unless blocked by another piece.
                            # Hence, the bottom conditional statement disregards the king. This also prevents any issues
                            # when computing king moves using this method.
                            if InBetween != "--" and InBetween != allyColor + 'K':
                                break
                        else:
                            sq.append([j, d, enemyColor + 'B'])
                            break

        # Check if Rook is attacking
        for j in rookLocation:
            if (j[0] - r == 0) or (j[1] - f == 0) and j != (r, f):
                distance = abs((j[0] - r) + (j[1] - f))
                if distance != 0:
                    d = ((j[0] - r) // distance, (j[1] - f) // distance)
                    if distance == 1:
                        sq.append([j, d])
                    else:
                        for i in range(1, 8):
                            rank = r + d[0] * i
                            file = f + d[1] * i
                            InBetween = self.board[rank][file]  # squares in between square (r, f) and Rook
                            if (rank, file) != j:
                                if InBetween != "--" and InBetween != allyColor + 'K':
                                    break
                            else:
                                sq.append([j, d, enemyColor + 'R'])
                                break

        # Check if Queen is attacking
        for j in queenLocation:
            if abs(j[0] - r) - abs(j[1] - f) == 0 and j != (r, f):
                distance = max(j[0], r) - min(j[0], r)
                if distance != 0:
                    d = ((j[0] - r) // abs(j[0] - r), (j[1] - f) // abs(j[1] - f))
                    if distance == 1:
                        sq.append([j, d])
                    else:
                        for i in range(1, 8):
                            rank = r + d[0] * i
                            file = f + d[1] * i
                            InBetween = self.board[rank][file]  # squares in between square (r, f) and Queen
                            if (rank, file) != j:
                                if InBetween != "--" and InBetween != allyColor + 'K':
                                    break
                            else:
                                sq.append([j, d, enemyColor + 'Q'])
                                break
            elif (j[0] - r == 0) or (j[1] - f == 0) and j != (r, f):
                distance = abs((j[0] - r) + (j[1] - f))
                if distance != 0:
                    d = ((j[0] - r) // distance, (j[1] - f) // distance)
                    if distance == 1:
                        sq.append([j, d])
                    else:
                        for i in range(1, 8):
                            rank = r + d[0] * i
                            file = f + d[1] * i
                            InBetween = self.board[rank][file]  # squares in between square (r, f) and Queen
                            if (rank, file) != j:
                                if InBetween != "--" and InBetween != allyColor + 'K':
                                    break
                            else:
                                sq.append([j, d, enemyColor + 'Q'])
                                break

        # Check if chosen square is being defended by enemy knights
        knightSq = [(r + 1, f + 2), (r + 2, f + 1), (r + 2, f - 1), (r + 1, f - 2), (r - 1, f - 2), (r - 2, f - 1),
                    (r - 2, f + 1), (r - 1, f + 2)]
        for j in knightSq:
            rank = j[0]
            file = j[1]
            onBoard = (0 <= rank <= 7) and (0 <= file <= 7)
            if onBoard:
                targetSq = self.board[rank][file]
                if targetSq == enemyColor + 'N':
                    sq.append([(rank, file), -1, enemyColor + 'N'])

        # Check if chosen square is defended by enemy pawns
        if self.whiteToMove:  # White's turn. Check if black pawns defend chosen square
            targetSq = self.board
            if (0 <= f - 1) and (targetSq[r - 1][f - 1] == 'bP'):  # Check left side of targetSq for pawn attack
                sq.append([(r - 1, f - 1), (-1, -1), 'bP'])
            elif (7 >= f + 1) and (targetSq[r - 1][f + 1] == 'bP'):  # Check right side of targetSq for pawn attack
                sq.append([(r - 1, f + 1), (-1, 1), 'bP'])
        else:  # Black's turn. Check if white pawns defend chosen square
            targetSq = self.board
            if (0 <= f - 1) and (targetSq[r + 1][f - 1] == 'wP'):  # Check right side of targetSq for pawn attack
                sq.append([(r + 1, f - 1), (1, -1), 'wP'])
            elif (7 <= f + 1) and (targetSq[r + 1][f + 1] == 'wP'):  # Check left side of targetSq for pawn attack
                sq.append([(r + 1, f + 1), (1, 1), 'wP'])

        # Check if enemy king is attacking square
        kingSq = [(r, f - 1), (r - 1, f - 1), (r - 1, f), (r - 1, f + 1), (r, f + 1), (r + 1, f + 1), (r + 1, f),
                  (r + 1, f - 1)]
        for i in range(8):
            onBoard = (0 <= kingSq[i][0] <= 7) and (0 <= kingSq[i][1] <= 7)
            if onBoard:
                rank = kingSq[i][0]
                file = kingSq[i][1]
                targetSq = self.board[rank][file]
                if targetSq == enemyColor + 'K':
                    sq.append([(rank, file), (rank - r, file - f), enemyColor + 'K'])
                    break
        return sq

    '''
    Get all possible pawn moves located on rank, file and add them to the list
    '''

    def get_pawn_moves(self, r, f, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0][0] == r and self.pins[i][0][1] == f:
                piecePinned = True
                pinDirection = self.pins[i][1]
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][f] == "--":  # 1 square pawn push
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, f), (r - 1, f), self.board))
                    if r == 6 and self.board[r - 2][f] == "--":  # 2 square pawn push
                        moves.append(Move((r, f), (r - 2, f), self.board))
            if f - 1 >= 0:  # captures to the left
                if self.board[r - 1][f - 1][0] == 'b':  # Opponents piece can be captured
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, f), (r - 1, f - 1), self.board))
                if self.moveLog:  # This is to prevent errors when first running script due to empty list
                    lastMove = self.moveLog[-1]
                    startRank = lastMove.startRank
                    endRank = lastMove.endRank
                    endFile = lastMove.endFile
                    moveTwoSquares = (startRank == 1) and (endRank == 3 == r)
                    enPassant = (lastMove.pieceMoved == 'bP') and moveTwoSquares and (endFile == f - 1)
                    if enPassant:
                        if not piecePinned or pinDirection == (-1, -1):
                            move = Move((r, f), (r - 1, f - 1), self.board)
                            move.enPassant = (r, f - 1)
                            move.pieceCaptured = self.board[r][f - 1]
                            self.enPassantMoves.append(move)
                            moves.append(move)
            if f + 1 <= 7:  # captures to the right
                if self.board[r - 1][f + 1][0] == 'b':  # Opponents piece can be captured
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, f), (r - 1, f + 1), self.board))
                if self.moveLog:  # This is to prevent errors when first running script due to empty list
                    lastMove = self.moveLog[-1]
                    startRank = lastMove.startRank
                    endRank = lastMove.endRank
                    endFile = lastMove.endFile
                    moveTwoSquares = (startRank == 1) and (endRank == 3 == r)
                    enPassant = (lastMove.pieceMoved == 'bP') and moveTwoSquares and (endFile == f + 1)
                    if enPassant:
                        if not piecePinned or pinDirection == (-1, 1):
                            move = Move((r, f), (r - 1, f + 1), self.board)
                            move.enPassant = (r, f + 1)
                            move.pieceCaptured = self.board[r][f + 1]
                            self.enPassantMoves.append(move)
                            moves.append(move)

        else:  # Black pawn moves
            if self.board[r + 1][f] == "--":  # 1 square pawn push
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, f), (r + 1, f), self.board))
                    if r == 1 and self.board[r + 2][f] == "--":  # 2 square pawn push
                        moves.append(Move((r, f), (r + 2, f), self.board))
            if f + 1 <= 7:  # Captures to the left
                if self.board[r + 1][f + 1][0] == 'w':  # Opponents piece can be captured
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, f), (r + 1, f + 1), self.board))
                if self.moveLog:  # This is to prevent errors when first running script due to empty list
                    lastMove = self.moveLog[-1]
                    startRank = lastMove.startRank
                    endRank = lastMove.endRank
                    endFile = lastMove.endFile
                    moveTwoSquares = (startRank == 6) and (endRank == 4 == r)
                    enPassant = (lastMove.pieceMoved == 'wP') and moveTwoSquares and (endFile == f + 1)
                    if enPassant:
                        if not piecePinned or pinDirection == (1, 1):
                            move = Move((r, f), (r + 1, f + 1), self.board)
                            move.enPassant = (r, f + 1)
                            move.pieceCaptured = self.board[r][f + 1]
                            self.enPassantMoves.append(move)
                            moves.append(move)
            if f - 1 >= 0:  # Captures piece to the right
                if self.board[r + 1][f - 1][0] == 'w':  # Opponents piece can be captured
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, f), (r + 1, f - 1), self.board))
                if self.moveLog:  # This is to prevent errors when first running script due to empty list
                    lastMove = self.moveLog[-1]
                    startRank = lastMove.startRank
                    endRank = lastMove.endRank
                    endFile = lastMove.endFile
                    moveTwoSquares = (startRank == 6) and (endRank == 4 == r)
                    enPassant = (lastMove.pieceMoved == 'wP') and moveTwoSquares and (endFile == f - 1)
                    if enPassant:
                        if not piecePinned or pinDirection == (1, -1):
                            move = Move((r, f), (r + 1, f - 1), self.board)
                            move.enPassant = (r, f - 1)
                            move.pieceCaptured = self.board[r][f - 1]
                            self.enPassantMoves.append(move)
                            moves.append(move)

    '''
    Get all possible knight moves located on rank, file and add them to the list
    '''

    def get_knight_moves(self, r, f, moves):
        if self.whiteToMove:  # White's turn
            allyColor = 'w'
        else:
            allyColor = 'b'

        # Check if Knight is pinned
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0][0] == r and self.pins[i][0][1] == f:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        if not piecePinned:
            knightMoves = [(r + 1, f + 2), (r + 2, f + 1), (r + 2, f - 1), (r + 1, f - 2), (r - 1, f - 2),
                           (r - 2, f - 1), (r - 2, f + 1), (r - 1, f + 2)]
            for i in range(8):
                onBoard = (0 <= knightMoves[i][0] <= 7) and (0 <= knightMoves[i][1] <= 7)
                if onBoard:
                    if self.board[knightMoves[i][0]][knightMoves[i][1]][0] != allyColor:
                        moves.append(Move((r, f), knightMoves[i], self.board))

    '''
    Get all possible bishop moves located on rank, file and add them to the list
    '''

    def get_bishop_moves(self, r, f, moves):
        if self.whiteToMove:  # White's turn
            enemyColor = 'b'
        else:
            enemyColor = 'w'

        # Check if pinned and what direction. Then generate moves accordingly
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0][0] == r and self.pins[i][0][1] == f:
                piecePinned = True
                pinDirection = self.pins[i][1]
                self.pins.remove(self.pins[i])
                break

        if not piecePinned or pinDirection == (-1, -1) or pinDirection == (1, 1):
            topLeft = min(r, f) + 1
            bottomRight = 8 - max(r, f)
            for i in range(1, topLeft):
                if self.board[r - i][f - i] == "--":
                    moves.append(Move((r, f), (r - i, f - i), self.board))
                elif self.board[r - i][f - i][0] == enemyColor:
                    moves.append(Move((r, f), (r - i, f - i), self.board))
                    break
                else:
                    break
            for i in range(1, bottomRight):
                if self.board[r + i][f + i] == "--":
                    moves.append(Move((r, f), (r + i, f + i), self.board))
                elif self.board[r + i][f + i][0] == enemyColor:
                    moves.append(Move((r, f), (r + i, f + i), self.board))
                    break
                else:
                    break
        if not piecePinned or pinDirection == (-1, 1) or pinDirection == (1, -1):
            topRight = min(r, 7 - f) + 1
            bottomLeft = 8 - max(r, 7 - f)
            for i in range(1, topRight):
                if self.board[r - i][f + i] == "--":
                    moves.append(Move((r, f), (r - i, f + i), self.board))
                elif self.board[r - i][f + i][0] == enemyColor:
                    moves.append(Move((r, f), (r - i, f + i), self.board))
                    break
                else:
                    break
            for i in range(1, bottomLeft):
                if self.board[r + i][f - i] == "--":
                    moves.append(Move((r, f), (r + i, f - i), self.board))
                elif self.board[r + i][f - i][0] == enemyColor:
                    moves.append(Move((r, f), (r + i, f - i), self.board))
                    break
                else:
                    break

    '''
    Get all possible rook moves located on rank, file and add them to the list
    '''

    def get_rook_moves(self, r, f, moves):
        if self.whiteToMove:  # White's turn
            enemyColor = 'b'
        else:
            enemyColor = 'w'

        # Check if pinned and what direction. Then generate moves accordingly
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0][0] == r and self.pins[i][0][1] == f:
                piecePinned = True
                pinDirection = self.pins[i][1]
                self.pins.remove(self.pins[i])
                break
        if not piecePinned or pinDirection == (1, 0) or pinDirection == (-1, 0):
            top = r + 1
            bottom = 8 - r
            for i in range(1, top):
                if self.board[r - i][f] == "--":
                    moves.append(Move((r, f), (r - i, f), self.board))
                elif self.board[r - i][f][0] == enemyColor:
                    moves.append(Move((r, f), (r - i, f), self.board))
                    break
                else:
                    break
            for i in range(1, bottom):
                if self.board[r + i][f] == "--":
                    moves.append(Move((r, f), (r + i, f), self.board))
                elif self.board[r + i][f][0] == enemyColor:
                    moves.append(Move((r, f), (r + i, f), self.board))
                    break
                else:
                    break
        if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
            left = f + 1
            right = 8 - f
            for i in range(1, left):
                if self.board[r][f - i] == "--":
                    moves.append(Move((r, f), (r, f - i), self.board))
                elif self.board[r][f - i][0] == enemyColor:
                    moves.append(Move((r, f), (r, f - i), self.board))
                    break
                else:
                    break
            for i in range(1, right):
                if self.board[r][f + i] == "--":
                    moves.append(Move((r, f), (r, f + i), self.board))
                elif self.board[r][f + i][0] == enemyColor:
                    moves.append(Move((r, f), (r, f + i), self.board))
                    break
                else:
                    break

    '''
    Get all possible queen moves located on rank, file and add them to the list
    '''

    def get_queen_moves(self, r, f, moves):
        # Check if pinned and what direction. Then generate moves accordingly
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0][0] == r and self.pins[i][0][1] == f:
                piecePinned = True
                pinDirection = self.pins[i][1]
                break

        rookDirections = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        if piecePinned:
            if pinDirection in rookDirections:
                self.get_rook_moves(r, f, moves)
            else:
                self.get_bishop_moves(r, f, moves)
        else:
            self.get_rook_moves(r, f, moves)
            self.get_bishop_moves(r, f, moves)

    '''
    Get all possible king moves located on rank, file and add them to the list
    '''

    def get_king_moves(self, r, f, moves):
        if self.whiteToMove:  # White's turn
            allyColor = 'w'
        else:
            allyColor = 'b'

        kingMoves = [(r, f - 1), (r - 1, f - 1), (r - 1, f), (r - 1, f + 1), (r, f + 1), (r + 1, f + 1), (r + 1, f),
                     (r + 1, f - 1)]
        for i in range(8):
            rank = kingMoves[i][0]
            file = kingMoves[i][1]
            onBoard = (0 <= rank <= 7) and (0 <= file <= 7)
            if onBoard:
                squareAttacked = self.square_under_attack(rank, file)
                allyPiece = self.board[rank][file][0] == allyColor
                if not (squareAttacked or allyPiece):
                    moves.append(Move((r, f), (rank, file), self.board))

        canCastle = self.canCastle[0] or self.canCastle[1]
        if canCastle:
            castleShort = self.canCastle[0]
            castleLong = self.canCastle[1]
            if castleShort:
                move = Move((r, f), (r, f + 2), self.board)
                move.castle = ((r, 7), (r, 5))
                self.castleMoves.append(move)
                moves.append(move)
            if castleLong:
                move = Move((r, f), (r, f - 2), self.board)
                move.castle = ((r, 0), (r, 3))
                self.castleMoves.append(move)
                moves.append(move)


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRank = startSq[0]
        self.startFile = startSq[1]
        self.endRank = endSq[0]
        self.endFile = endSq[1]
        self.pieceMoved = board[self.startRank][self.startFile]
        self.pieceCaptured = board[self.endRank][self.endFile]
        self.enPassant = ()  # Holds location of pawn being captured
        # Holds start and end location of rook being castled ((startRank, startFile), (endRank, endFile))
        self.castle = ()
        self.castlingRights = ()  # This will preserve the castling rights of the player if move in undone
        self.moveID = self.startRank * 1000 + self.startFile * 100 + self.endRank * 10 + self.endFile
        # print(self.moveID)

    '''
    Overwriting the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        # you can add to make this like real chess notation
        return self.get_rank_file(self.startRank, self.startFile) + self.get_rank_file(self.endRank, self.endFile)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
