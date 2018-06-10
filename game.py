"""
To run the program on command line type: python3 game.py <file_name>

Cheating Scenarios:
1. Stealing money from the bank (ie. paying for property/other players after going bankrupt)
2. Playing out of turn
3. Paying rent not equal to 50% of property value 

Assumptions:

1. If the action is purchase and the property is already owned, it will be purchased by the current player
2. Rather than denying a purchase/paying rent by a bankrupt player, the possibility of player going bankrupt is avoided. (If a player has 75$ in
account and tries to purchase/pay rent upto 100$, then the transaction is not made complete, and regarded as cheating.)

"""


import json
import sys
from pathlib import Path

#class Player to store the player details
class player:
    def __init__(self, name):
        self.name = name
        ## Variable to keep track of a players money
        self.money = 500
        ## Variable to keep track of a players moves
        self.moves = 0
        ## Variable to keep track of places owned by a player
        self.pplace = []
        ## Flag Variable to represent a cheat
        self.cheat = False
        ## Rent acquired by each player
        self.rentAcquired = 0

    def __repr__(self):
        return self.name


#class place to store the property details
class place:
    def __init__(self, name, owner, cost):
        self.name = name
        self.owner = owner
        self.cost = cost
        self.rent = 0.5*self.cost

    def __repr__(self):
        return self.name


##Function to find the next player in the execution sequence. Executes in a round-robin method flow
def findNextPlayer(curr_player, playerlist):
    
    ind = playerlist.index(curr_player)+1
    ind = ind%len(playerlist)
    
    ep = playerlist[ind]
    return ep

# Dictionary of player class objects
players = {}
# List to keep track of player order
playerlist = []
# Dictionary of place class objects
places = {}

#To calculate the current round
round = 0
#To identiify the cheater
cheater = ""
#To calculate the no of players who exhausted their accounts
zeros = 0

## If JSON file is not given as input
if(len(sys.argv) == 1):
    print("Enter json file name")
    sys.exit()

file_name = sys.argv[1]
my_file = Path(file_name)

#To check if the file is present or not
if not my_file.is_file():
    print("Enter valid JSON file name")
    sys.exit()
expected_player = ""

##To initially fill the players list
def fillPlayers():
    with open(file_name) as f:
        for line in f:
            input = json.loads(line)
            input['player'] = input['player'].encode('ascii','ignore')
            if input['player'] not in players.keys():
                playerlist.append(input['player'])
                players[input['player']] = player(input['player'])

fillPlayers()

with open(file_name) as f:
    for line in f:
        input = json.loads(line)
        ## Convert Player and Place name from Unicode to ASCII
        input['player'] = input['player'].encode('ascii','ignore')
        input['landed_on'] = input['landed_on'].encode('ascii','ignore')
        curr_player = input['player']

        
        ## Player Plays Out of Turn - Check this only in rounds that follow player creation
        
        if round >= len(players):
            if curr_player != expected_player:
                players[input['player']].cheat = True
                cheater = input['player'].decode("utf-8") + " - " + " Player played out of turn in round "+ str(round+1)
                break
        
        players[input['player']].moves += int(input['roll'])
        ## Check if player has crossed 40 moves
        if players[input['player']].moves >= 40:
            players[input['player']].moves -= 40
            if(players[input['player']].money == 0):
            	zeros -= 1
            players[input['player']].money += 200

        ## Player purchases property
        if input['action'] == 'purchase' :
            if input['landed_on'] not in places.keys():
            ## Create Place
                places[input['landed_on']] = place(input['landed_on'], input['player'], input['price'])


            ##Checking if player will go bankrupt or not
            if players[input['player']].money - int(input['price']) < 0:
                players[input['player']].cheat = True
                cheater = input['player'].decode("utf-8")+" - "+"Stealing money from the bank in round "+str(round+1)
                break
            ## Player Actions
            players[input['player']].money -= int(input['price'])
            players[input['player']].pplace.append(input['landed_on']) 

            #To check if the purchase was not the initial one for the property
            if(places[input['landed_on']].owner != input['player']):

                #To check if the owner was exhausted. To keep track of bankrupt players
                if(players[places[input['landed_on']].owner].money == 0):
                    zeros -= 1
                players[places[input['landed_on']].owner].money += int(input['price'])
                places[input['landed_on']].owner = input['player']

            #Check if all except one has exhausted
            if players[input['player']].money == 0:
            	zeros +=1								
            	if(zeros == len(players)-1 and round >= len(players)):
            	   break

        ## Player pays rent
        if input['action'] == 'paid rent':
            ## Check if rent is correct
            ##Checking if player will go bankrupt or not
            if players[input['player']].money - int(input['price']) < 0:
                players[input['player']].cheat = True
                cheater = input['player'].decode("utf-8")+" - "+"Stealing money from the bank in round "+str(round+1)
                break

            #To check if the rent is lesser than 50% of price 
            if input['price'] < places[input['landed_on']].rent:
                players[input['player']].cheat = True
                cheater = input['player'].decode("utf-8")+" - "+"Paid Incorrect Rent in round "+str(round+1)
                break
            #Player updates account
            players[input['player']].money -= int(input['price'])

            #Check if owner was exhausted
            if(players[places[input['landed_on']].owner].money == 0):
            		zeros -= 1

            #Rent Actions
            players[places[input['landed_on']].owner].money += int(input['price'])
            players[places[input['landed_on']].owner].rentAcquired += int(input['price'])

            #Check if all except one player have exhausted
            if players[input['player']].money == 0:
            	zeros +=1
            	if(zeros == len(players)-1 and round >= len(players)):
            		break

        #Check if first round is over
        if(round+1 >= len(playerlist)):
            #Finding the expected player for the next iteration
            expected_player = findNextPlayer(curr_player, playerlist)
        round += 1

## Finding the Winner and printing the summary
max = 0
winner = ""
for key in players:
	if players[key].cheat == True:
		continue
	print (players[key].name.decode()," has $",players[key].money,"owns ",players[key].pplace," and acquired ","$",players[key].rentAcquired,"in rent.")
	if players[key].money > max:
		winner = players[key].name
		max = players[key].money

print ("Winner is "+ winner.decode() + " with a final amount of " + str(max) + ".")
## Printing the Cheater if there is one
if(cheater != ""):
	print ("There was a cheater in the game,")
	print (cheater)