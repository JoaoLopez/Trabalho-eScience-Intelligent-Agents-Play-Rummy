from collections import deque
import numpy as np
import random

from numpy.matrixlib.defmatrix import matrix

suitDict = {"S": 0, "H": 1, "C": 2, "D":3}

# Helper functions for matrix representation of cards

####################É DETERMINÍSTICA
# Gets index of first occuring card in a hand (row-wise)
def getFirstCard(matrix, shp):
    for i in range(shp[0]):
        for j in range(shp[1]):
            if matrix[i][j] == 1:
                return (i, j)

####################É DETERMINÍSTICA
# Gets all indexes of same value for same-value melds
def getSameValue(matrix, index):
    j = index[1]
    result = []
    for i in range(4):
        if i != index[0] and matrix[i][j] == 1:
            result.append((i, j))
    return result

# Entity classes

class Card:
    def __init__(self, val, st):
        self.value = val  # actual number on card
        self.suit = st
        self.points = val  # point value of card
        if val == -1:  # joker cards have no points
            self.points = 0
        elif val == 1 or val > 10:  # ace and face cards
            self.points = 10
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        strVal = ["A"] + [str(x) for x in range(2, 11)] + ["J", "Q", "K"]
        if self.value != -1:
            return self.suit + strVal[self.value - 1]
        else:
            return self.suit  # will return "JK1" or "JK2" for joker cards
    
    def __eq__(self, object) -> bool:
        if not isinstance(object, Card):
            return False
        return self.value==object.value and self.suit==object.suit
    
    def __ne__(self, object) -> bool:
        return not self.__eq__(object)
    
    def __hash__(self) -> int:
        return hash(str(self))

class Deck:
    def __init__(self):
        self.cards = []
        # each card is represented by a letter for suit + number for value. A is 1, J, Q, K are 11, 12, 13 respectively
        for s in suitDict.keys():
            for v in range(1, 14):
                self.cards.append(Card(v, s))
        self.cards.append(Card(-1, "JK1"))
        self.cards.append(Card(-1, "JK2"))
        self.joker = None
    
    def __repr__(self) -> str:
        return "Deck()"
    
    def __str__(self) -> str:
        output = "Deck: "
        for card in self.cards:
            output += str(card) + "    "
        return output
    
    def shuffle(self, seed):
        if seed:
            random.seed(seed)
        random.shuffle(self.cards)
    
    def draw(self):
        return self.cards.pop()  # direction doesn't matter so pop from end
    
    def returnToDeck(self, card):
        self.cards.append(card)

class DiscardPile:
    def __init__(self):
        self.cards = deque()  # acts as a stack
    
    def __repr__(self) -> str:
        return "DiscardPile()"
    
    def __str__(self) -> str:
        output = "Discard Pile: "
        for card in self.cards:
            output += str(card) + "    "
        return output
    
    def draw(self):
        return self.cards.pop()
    
    def discard(self, card):
        self.cards.append(card)

class Hand:
    def __init__(self):
        self.cards = []
        self.cardMatrix = np.zeros((4,13))
        self.compMatrix = np.zeros((4,13))  # used for checking if game is complete
        self.jokers = 0
        self.rummyJokerVal = -1
    
    def __repr__(self) -> str:
        return "Hand()"
    
    def __str__(self) -> str:
        output = ""
        for card in self.cards:
            output += str(card) + "    "
        return output
    
    def setJoker(self, jokerVal):
        if jokerVal == -1:  # joker card is rummy joker drawn at start of round
            return
        for i in range(4):
            self.cardMatrix[i][jokerVal-1] = -1
            self.compMatrix[i][jokerVal-1] = -1
        self.rummyJokerVal = jokerVal
    
    def draw(self, card):
        self.cards.append(card)
        if card.value != -1 and card.value != self.rummyJokerVal:
            self.cardMatrix[suitDict[card.suit]][card.value-1] = 1
        else:
            self.jokers += 1
    
    # def discard(self, val):
    #     for index, card in enumerate(self.cards):
    #         if card.value == val:
    #             if val != -1:
    #                 self.cardMatrix[suitDict[card.suit]][card.value-1] = 0
    #             else:
    #                 self.jokers -= 1
    #             return self.cards.pop(index)
    #     return "error"

    def discard(self, index):
        if self.cards[index].value != -1:
            self.cardMatrix[suitDict[self.cards[index].suit]][self.cards[index].value-1] = 0
        else:
            self.jokers -= 1
        return self.cards.pop(index)

    def checkMelds(self, matrix=None, jkr=None, pureFlag = 0, straightCount = 0):  # only checks for win state for now, returns bool if game is won
        # TODO: implement pure and straight checks
        try:
            if matrix==None:
                matrix = self.cardMatrix.copy()
        except:
            pass
        try:
            if jkr==None:
                jkr = self.jokers
        except:
            pass
        # Recursive function
        # find first 1 in matrix, check all melds (including chances+jokers, reduce num of jokers in this case) using this card
        # for each meld, recursive call checkMelds with new matrix, without the cards in the meld being considered
        # if no chances => return false, backtrack one step
        # base case => matrix is all 0s, return true
        # end of recursion case => if all melds lead to false, return false

        # Base case:
        if (matrix==self.compMatrix).all():
            if straightCount > 1 and pureFlag:
                print("Note: Additional jokers in hand may be excluded in following melds")
                return True
            else:
                return False
        
################ESSA PARTE É DETERMINÍSTICA
        # Recursive case
        # search for straight melds on right side only, prevents overlap
        shp = np.shape(matrix)
        i, j = getFirstCard(matrix, shp)
        if j == 12:  # king
            right1 = right2 = right3 = (False, (i,j))
        elif j == 11:  # queen
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][0]==1), (i, 0))
            right3 = (False, (i, j))
        elif j == 10:  # jack:
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][j+2]==1), (i, j+2))
            right3 = (bool(matrix[i][0]==1), (i, 0))
        else:
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][j+2]==1), (i, j+2))
            right3 = (bool(matrix[i][j+3]==1), (i, j+3))
        
        melds = []
        # no elif anywhere in case the other card needs to be used for something; considers all cases

        # straight melds
        # pure highest in order so it's considered first if possible
        if right1[0] and right2[0]:
            if right3[0]:
                melds.append([[(i, j), right1[1], right2[1], right3[1]], 1, 1])  # priority 1
            melds.append([[(i, j), right1[1], right2[1]], 1, 1])  # priority 2
            if jkr:
                melds.append([[(i, j), right1[1], right2[1], "JKR"], 0, 1])  # priority 3
        if right1[0] and jkr:
            if right3[0]:
                melds.append([[(i, j), right1[1], "JKR", right3[1]], 0, 1])  # priority 4
            melds.append([[(i, j), right1[1], "JKR"], 0, 1])  # priority 5
        if right2[0] and jkr:
            if right3[0]:
                melds.append([[(i, j), "JKR", right2[1], right3[1]], 0, 1])  # priority 6
            melds.append([[(i, j), "JKR", right2[1]], 0, 1])  # priority 7
        if jkr > 1:
            if right3[0]:
                melds.append([[(i, j), "JKR", "JKR", right3[1]], 0, 1])  # priority 8
            melds.append([[(i, j), "JKR", "JKR"], 0, 1])  # priority 9

        # same value melds
        j_vals = getSameValue(matrix, (i, j))
        if len(j_vals) == 3:
            melds.append([[(i, j), j_vals[0], j_vals[1], j_vals[2]], 0, 0])  # priority 10
            melds.append([[(i, j), j_vals[0], j_vals[1]], 0, 0])  # priority 11
            melds.append([[(i, j), j_vals[2], j_vals[1]], 0, 0])  # priority 12
            melds.append([[(i, j), j_vals[0], j_vals[2]], 0, 0])  # priority 13
            if jkr:
                melds.append([[(i, j), "JKR", j_vals[1], j_vals[2]], 0, 0])  # priority 14
                melds.append([[(i, j), j_vals[0], "JKR", j_vals[2]], 0, 0])  # priority 15
                melds.append([[(i, j), j_vals[0], j_vals[1], "JKR"], 0, 0])  # priority 16
            if jkr > 1:
                melds.append([[(i, j), j_vals[0], "JKR", "JKR"], 0, 0])  # priority 17
                melds.append([[(i, j), j_vals[1], "JKR", "JKR"], 0, 0])  # priority 18
                melds.append([[(i, j), j_vals[2], "JKR", "JKR"], 0, 0])  # priority 19
        elif len(j_vals) == 2:
            melds.append([[(i, j), j_vals[0], j_vals[1]], 0, 0])  # priority 10
            if jkr:
                melds.append([[(i, j), j_vals[0], j_vals[1], "JKR"], 0, 0])  # priority 11
                melds.append([[(i, j), "JKR", j_vals[1]], 0, 0])  # priority 12
                melds.append([[(i, j), j_vals[0], "JKR"], 0, 0])  # priority 13
        elif len(j_vals) == 1 and jkr:
            melds.append([[(i, j), j_vals[0], "JKR"], 0, 0])  # priority 10

        # print(melds)  # for debugging purposes only
##############################################
        for item in melds:  # if no melds, following block is skipped and it returns false
            meld = item[0]
            matrixCopy = matrix.copy()
            jkrCopy = jkr
            pureCopy = pureFlag
            straightCopy = straightCount
            if item[1]:
                pureCopy += 1
            if item[2]:
                straightCopy += 1
            for index in meld:
                if index == "JKR":
                    jkrCopy -= 1
                else:
                    matrixCopy[index[0]][index[1]] = 0
            if self.checkMelds(matrixCopy, jkrCopy, pureCopy, straightCopy):  # recursive call
                print(meld)
                return True  # dfs match found
        return False  # no match in this dfs branch, backtracks one step
    
    def calculatePoints(self, matrix=None, jkr=None, pureFlag=0, pts=0, fullHand=None):
        try:
            if matrix==None:
                matrix = self.cardMatrix.copy()
        except:
            pass
        try:
            if jkr==None:
                jkr = self.jokers
        except:
            pass
        try:
            if fullHand==None:
                fullHand = 0
                for s in suitDict.keys():
                    i = suitDict[s]
                    for j in range(13):
                        if matrix[i][j]==1:
                            fullHand += Card(j+1, s).points
        except:
            pass

        # Recursive function
        # set "fullHand" to full points of hand if none
        # find first 1 in matrix, check all melds (including chances+jokers, reduce num of jokers in this case) using this card
        # to melds, always add just the card itself, in which case you increment "pts" by the card's points (this condition accounts for when card is left alone)
        # set min_temp to fullHand
        # for each meld, recursive call calculatePoints with new matrix, without the cards in the meld being considered
        # if value returned is less than min_temp, replace min_temp. Else, continue.
        # on evaluating all options, return min_temp
        # base case -> if matrix is all 0s: if pureFlag is 1, return pts. Else, return minpts.

        # Base case:
        if (matrix==self.compMatrix).all():
            if pureFlag:
                return pts
            else:
                return fullHand
        
#######################ESSA PARTE É DETERMINÍSTICA
        # Recursive case
        # search for straight melds on right side only, prevents overlap
        shp = np.shape(matrix)
        i, j = getFirstCard(matrix, shp)
        if j == 12:  # king
            right1 = right2 = right3 = (False, (i,j))
        elif j == 11:  # queen
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][0]==1), (i, 0))
            right3 = (False, (i, j))
        elif j == 10:  # jack:
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][j+2]==1), (i, j+2))
            right3 = (bool(matrix[i][0]==1), (i, 0))
        else:
            right1 = (bool(matrix[i][j+1]==1), (i, j+1))
            right2 = (bool(matrix[i][j+2]==1), (i, j+2))
            right3 = (bool(matrix[i][j+3]==1), (i, j+3))
        
        melds = []
        # no elif anywhere in case the other card needs to be used for something; considers all cases

        # straight melds
        # pure highest in order so it's considered first if possible
        if right1[0] and right2[0]:
            if right3[0]:
                melds.append([[(i, j), right1[1], right2[1], right3[1]], 1])  # priority 1
            melds.append([[(i, j), right1[1], right2[1]], 1])  # priority 2
            if jkr:
                melds.append([[(i, j), right1[1], right2[1], "JKR"], 0])  # priority 3
        if right1[0] and jkr:
            if right3[0]:
                melds.append([[(i, j), right1[1], "JKR", right3[1]], 0])  # priority 4
            melds.append([[(i, j), right1[1], "JKR"], 0])  # priority 5
        if right2[0] and jkr:
            if right3[0]:
                melds.append([[(i, j), "JKR", right2[1], right3[1]], 0])  # priority 6
            melds.append([[(i, j), "JKR", right2[1]], 0])  # priority 7
        if jkr > 1:
            if right3[0]:
                melds.append([[(i, j), "JKR", "JKR", right3[1]], 0])  # priority 8
            melds.append([[(i, j), "JKR", "JKR"], 0])  # priority 9

        # same value melds
        j_vals = getSameValue(matrix, (i, j))
        if len(j_vals) == 3:
            melds.append([[(i, j), j_vals[0], j_vals[1], j_vals[2]], 0])  # priority 10
            melds.append([[(i, j), j_vals[0], j_vals[1]], 0])  # priority 11
            melds.append([[(i, j), j_vals[2], j_vals[1]], 0])  # priority 12
            melds.append([[(i, j), j_vals[0], j_vals[2]], 0])  # priority 13
            if jkr:
                melds.append([[(i, j), "JKR", j_vals[1], j_vals[2]], 0])  # priority 14
                melds.append([[(i, j), j_vals[0], "JKR", j_vals[2]], 0])  # priority 15
                melds.append([[(i, j), j_vals[0], j_vals[1], "JKR"], 0])  # priority 16
            if jkr > 1:
                melds.append([[(i, j), j_vals[0], "JKR", "JKR"], 0])  # priority 17
                melds.append([[(i, j), j_vals[1], "JKR", "JKR"], 0])  # priority 18
                melds.append([[(i, j), j_vals[2], "JKR", "JKR"], 0])  # priority 19
        elif len(j_vals) == 2:
            melds.append([[(i, j), j_vals[0], j_vals[1]], 0])  # priority 10
            if jkr:
                melds.append([[(i, j), j_vals[0], j_vals[1], "JKR"], 0])  # priority 11
                melds.append([[(i, j), "JKR", j_vals[1]], 0])  # priority 12
                melds.append([[(i, j), j_vals[0], "JKR"], 0])  # priority 13
        elif len(j_vals) == 1 and jkr:
            melds.append([[(i, j), j_vals[0], "JKR"], 0])  # priority 10

        # print(melds)  # for debugging purposes only
        melds.append([[(i, j)], 0])  # case where card is added to points and not considered for future melds
        min_temp = fullHand
##############################################

        for item in melds:
            meld = item[0]
            matrixCopy = matrix.copy()
            jkrCopy = jkr
            pureCopy = pureFlag
            ptsCopy = pts
            if item[1]:
                pureCopy += 1
            if len(meld) == 1:
                for s in suitDict.keys():
                    if suitDict[s] == meld[0][0]:
                        ptsCopy += Card(meld[0][1]+1, s).points
            for index in meld:
                if index == "JKR":
                    jkrCopy -= 1
                else:
                    matrixCopy[index[0]][index[1]] = 0
            min_temp = min(min_temp, self.calculatePoints(matrixCopy, jkrCopy, pureCopy, ptsCopy, fullHand))  # recursive call
        return min_temp
