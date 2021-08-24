#main class, handles user input and displays game state
import pygame
from ChessBot import ChessEngine, SmartMoveFinder
pygame.init()

BOARD_WIDTH = BOARD_HEIGHT = 512

MOVE_LOG_PANEL_WIDTH = 250

MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT

DIMENSION = 8 #8 by 8 board

SQUARE_SIZE = BOARD_HEIGHT // DIMENSION

MAX_FPS = 15

IMAGES = {}

'''
Initializing images.
'''

def loadImages():
    pieces = ["wP", 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    moveLogFont = pygame.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.currentState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable to increase efficiency
    animate = False #flag for when we should animate

    loadImages()
    running = True
    sqSelected = () #tuple of last square clicked
    playerClicks = [] #keeps track of player clicks(two tuples, to track move)
    gameOver = False
    playerOne = True # if a human is playing white, then true, if AI is white, then false
    playerTwo = True #can pit two AI against each o ther if both are false
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            #mouse event handlers
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos() # location of mouse
                    col = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE
                    if sqSelected == (row,col) or col >= 8: #exact same square or move log section
                        sqSelected = () #deselect
                        playerClicks = []        #clear player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: #move is made
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move ==validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks  = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key event handlers
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z: #undo button is Z
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == pygame.K_r: #reset when 'r' is pressed
                    gs = ChessEngine.currentState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)

            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves,sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            if gs.stalemate:
                text = 'Stalemate'
                drawEndGameText(screen,text)
            else:
                if gs.whiteToMove:
                    text = 'Black wins by checkmate'
                    drawEndGameText(screen, text)
                else:
                    text = 'White wins by checkmate'
                    drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        pygame.display.flip()

#Highlights square selected and moves for piece selected

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected !=():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight selected square
            s = pygame.Surface((SQUARE_SIZE,SQUARE_SIZE))
            s.set_alpha(100) #transparency value
            s.fill(pygame.Color('blue'))
            screen.blit(s,(c*SQUARE_SIZE,r*SQUARE_SIZE))
            s.fill(pygame.Color('yellow'))
            for move in validMoves:
                if move.startRow ==r and move.startCol == c:
                    screen.blit(s, (SQUARE_SIZE*move.endCol, SQUARE_SIZE*move.endRow))

#generates graphics of game
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves, sqSelected)
    drawPieces(screen,gs.board)
    drawMoveLog(screen,gs, moveLogFont)


def drawBoard(screen):
    global colors
    colors = (pygame.Color(235,235,208), pygame.Color(119,148,85))
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            pygame.draw.rect(screen,color,pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(c*SQUARE_SIZE,r*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))


def animateMove(move,screen,board,clock):
    global colors
    coords = [] #list of coordinations for animation
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 2 # frame speed
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen,color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = pygame.Rect(move.endCol * SQUARE_SIZE, enPassantRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving pieces
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)

def drawMoveLog(screen, gs, font):
    moveLogRect = pygame.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []     #modify this later
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[ i + 1])   + "  "
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0,len(moveTexts), movesPerRow):
        text = ''
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, pygame.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing




def drawEndGameText(screen,text):
    font = pygame.font.SysFont("Helvetica",32,True,False)
    textObject = font.render(text,0,pygame.Color('Black'))
    textLocation = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text,0,pygame.Color("Black"))
    screen.blit(textObject,textLocation.move(2,2))





if __name__ == "__main__":
    main()