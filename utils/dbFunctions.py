import sqlite3, random
f = "../data/game.db"

with open("blackcards.txt") as fb:
    blacks = fb.readlines()
blacks = [x.strip() for x in blacks]

with open("whitecards.txt") as fb:
    whites = fb.readlines()
whites = [x.strip() for x in whites] 

#validate 
def validate(user, password):
    db = sqlite3.connect(f)
    c = db.cursor()
    found = c.execute("SELECT count(*) FROM users WHERE user = '%s' AND password = '%s'" % (user, password)).fetchall()
    db.commit()
    db.close()
    return (found[0][0] == 1)

#checks for repeated usernames
def hasUsername(username):
    db = sqlite3.connect(f)
    c = db.cursor()
    found = c.execute("SELECT count(*) FROM users WHERE user = '%s'" % (username)).fetchall()
    db.commit()
    db.close()
    return (found[0][0] == 1)

#generates a gameID
def newGameID():
    db = sqlite3.connect(f)
    c = db.cursor()
    max = c.execute("SELECT MAX(gameID) FROM games").fetchall()
    db.commit()
    db.close()
    if max[0][0] is None:
        return 0
    return max[0][0] + 1

#adds user to users table
def addUser(user, password):
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute("INSERT INTO users VALUES('%s', '%s')" % (user, password))
    db.commit()
    db.close()

#adds user who created to games with new gameID and sets user to dictator; adds white and black decks with gameID
def addGame(user, total, goal):
    db = sqlite3.connect(f)
    c = db.cursor()
    id = newGameID()
    c.execute("INSERT INTO games VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, user, 0, 1, 0, total, goal, 0))
    for each in whites:
        c.execute("INSERT INTO whiteDecks VALUES('%s', '%s')" % (id, each))
    for each in blacks:
        c.execute("INSERT INTO blackDecks VALUES('%s', '%s')" % (id, each))
    db.commit()
    db.close()

#adds user to games
def addPlayer(gameID, user):
    db = sqlite3.connect(f)
    c = db.cursor()
    total = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][5]
    goal = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][6]
    c.execute("INSERT INTO games VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (gameID, user, 0, 0, 0, total, goal, 0))
    count = c.execute("SELECT count(*) FROM games WHERE gameID = '%s'" % (each[0])).fetchall()[0][0]
    if count == total:
        c.execute("UPDATE games SET status = '%s' WHERE gameID = '%s'" % (1, gameID))
    db.commit()
    db.close()

#chooses black card randomly and removes from deck; adds to cardsOnBoard
def drawBlack(gameID,user):
    db = sqlite3.connect(f)
    c = db.cursor()
    cards = c.execute("SELECT * FROM blackDecks WHERE gameID = '%s'" % (gameID)).fetchall()
    chosen = (random.choice(cards))
    c.execute("DELETE FROM blackDecks WHERE gameID = '%s' AND card = '%s'" % (chosen[0], chosen[1]))
    c.execute("INSERT INTO cardsOnBoardBlack VALUES ('%s', '%s', '%s')" % (gameID, user, chosen[1]))
    db.commit()
    db.close()

#chooses white card randomly and removes from deck; adds to userCards
def drawWhite(gameID,user):
    db = sqlite3.connect(f)
    c = db.cursor()
    cards = c.execute("SELECT * FROM whiteDecks WHERE gameID = '%s'" % (gameID)).fetchall()
    chosen = (random.choice(cards))
    c.execute("DELETE FROM whiteDecks WHERE gameID = '%s' AND card = '%s'" % (chosen[0], chosen[1]))
    c.execute("INSERT INTO userCards VALUES ('%s', '%s', '%s')" % (gameID, user, chosen[1]))
    db.commit()
    db.close()

#given a card, deletes from userDecks and adds to cardsOn Board
def chooseCardToPlay(gameID,user,card):
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute("DELETE FROM userCards WHERE gameID = '%s' AND user = '%s' AND card = '%s'" % (gameID, user, card))
    c.execute("INSERT INTO cardsOnBoardWhite VALUES('%s','%s','%s')" % (gameID, user, card))
    db.commit()
    db.close()

    
#given a winning card, finds player who played it, updates their score, clears cardsOnBoard for that game, calls newDictator function
def chooseWinner(gameID, card):
    db = sqlite3.connect(f)
    c = db.cursor()
    player = c.execute("SELECT * FROM cardsOnBoardWhite WHERE gameID = '%s' AND card = '%s'" % (gameID, card)).fetchall()[0][1]
    score = c.execute("SELECT * FROM games WHERE gameID = '%s' AND user = '%s'" % (gameID, player)).fetchall()[0][2]
    c.execute("UPDATE games SET score = '%s' WHERE gameID = '%s' AND user = '%s'" % (score+1, gameID, player))
    c.execute("UPDATE games SET roundDone = 1 WHERE gameID = '%s'" % (gameID))
    c.execute("DELETE FROM cardsOnBoardWhite WHERE gameID = '%s'" % (gameID))
    c.execute("DELETE FROM cardsOnBoardBlack WHERE gameID = '%s'" % (gameID))
    #newDictator(gameID)
    if gameEnded(gameID):
        c.execute("UPDATE games SET status = '%s' WHERE gameID = '%s'" % (2, gameID))
    db.commit()
    db.close()

#determines if everyone has played a card
def playedCard(gameID):
    db = sqlite3.connect(f)
    c = db.cursor()
    players = c.execute("SELECT count(*) FROM games WHERE gameID = '%s'" % (gameID)).fetchall()
    cards = c.execute("SELECT count(*) FROM cardsOnBoardWhite WHERE gameID = '%s'" % (gameID)).fetchall()
    db.commit()
    db.close()
    return players[0][0]-1 == cards[0][0]

#sets next player as dictator
#def newDictator(gameID):

#returns cards of user
def cardsInDeck(gameID, user):
    db = sqlite3.connect(f)
    c = db.cursor()
    cards = []
    lines = c.execute("SELECT * FROM userCards WHERE gameID = '%s' AND user = '%s'" % (gameID, user)).fetchall()
    db.commit()
    db.close()
    for each in lines:
        cards.append(each[2])
    return cards

#returns boolean to check if game is over
def gameEnded(gameID):
    db = sqlite3.connect(f)
    c = db.cursor()
    goal = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][6]
    count = c.execute("SELECT count(*) FROM games WHERE gameID = '%s' AND score = '%s'" % (gameID, goal)).fetchall()[0][0]
    db.commit()
    db.close()
    print count
    return count > 0

#way to stop game when someone get certain amount of points

#checks to see if enough people joined game
def enoughPeople(gameID):
    db = sqlite3.connect(f)
    c = db.cursor()
    total = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][5]
    count = c.execute("SELECT count(*) FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][0]
    db.commit()
    db.close()
    return count == total

#checks to see if game is full



#way to read cards on text file  and put them in a list



#returns if winner has been chosen for the round
def winnerChosen(gameID):
    db = sqlite3.connect(f)
    c = db.cursor()
    bool = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (gameID)).fetchall()[0][4]
    c.execute("UPDATE games SET roundDone = '%s' WHERE gameID = '%s'" % (0, gameID))
    db.commit()
    db.close()
    return bool == 1

#initial draw x number of cards

#return all white cards on deck
def getWhite(gameID, user):
    db = sqlite3.connect(f)
    c = db.cursor()
    cards = []
    lines = c.execute("SELECT * FROM cardsOnBoardWhite WHERE gameID = '%s' AND user = '%s'" % (gameID, user)).fetchall()
    db.commit()
    db.close()
    for each in lines:
        cards.append(each[2])
    return cards

#return all black cards on deck
def getBlack(gameID):
    db = sqlite3.connect(f)
    c = db.cursor()
    cards = []
    lines = c.execute("SELECT * FROM cardsOnBoardBlack WHERE gameID = '%s' AND user = '%s'" % (gameID, user)).fetchall()
    db.commit()
    db.close()
    for each in lines:
        cards.append(each[2])
    return cards

def getCurrent(user):
    db = sqlite3.connect(f)
    c = db.cursor()
    lines = c.execute("SELECT * FROM games WHERE user = '%s' AND status = '%s' AND status = '%s'" % (user, 0, 1)).fetchall()
    result = []
    for each in lines:
        d = {}
        d["gameID"] = each[0]
        players = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (each[0])).fetchall()
        d["player"] = player[0][1]
        count = c.execute("SELECT count(*) FROM games WHERE gameID = '%s'" % (each[0])).fetchall()[0][0]
        d["current"] = count
        d["total"] = each[5]
        playersString = ""
        for line in players:
            playersString += line[1] + ", "
        d["players"] = playersString
        d["goal"] = each[6]
        result.append(d)
    db.commit()
    db.close()

#def getJoin(user):

def getFinished():
    db = sqlite3.connect(f)
    c = db.cursor()
    lines = c.execute("SELECT * FROM games WHERE status = '%s'" % (user, 2)).fetchall()
    result = []
    for each in lines:
        d = {}
        d["gameID"] = each[0]
        players = c.execute("SELECT * FROM games WHERE gameID = '%s'" % (each[0])).fetchall()
        d["player"] = player[0][1]
        count = c.execute("SELECT count(*) FROM games WHERE gameID = '%s'" % (each[0])).fetchall()[0][0]
        d["current"] = count
        d["total"] = each[5]
        playersString = ""
        for line in players:
            playersString += line[1] + ", "
        d["players"] = playersString
        d["goal"] = each[6]
        result.append(d)
    db.commit()
    db.close()

#return all white cards in user's deck
    
#addUser("Jim","password")
#addUser("Bob","password")
#addUser("Mary","password")
#addGame("Jim")
#addPlayer(0, "Bob")
#addPlayer(0, "Sam")
#drawBlack(0, "Jim")
#drawWhite(0, "Bob")
#drawWhite(0, "Bob")
#chooseCardToPlay(0,"Bob","A foul mouth.")
#chooseCardToPlay(0,"Mary","c")
#print playedCard(0)
#print cardsInDeck(0,"Bob")
#chooseWinner(0,"A foul mouth.")
#print winnerChosen(0)
#print enoughPeople(0)
db = sqlite3.connect(f)
c = db.cursor()
c.execute("SELECT * FROM games")
data = c.fetchall()
#print(data)