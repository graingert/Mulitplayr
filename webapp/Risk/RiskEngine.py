import random
import copy
import RiskElements
import RiskInterface

class RiskGame(object):

	"""-----------Core functions-----------"""
	
	def __init__(self, riskInterface):
		self.currentPlayer = None
		self.playerList = []
	
		self.territories = {}
		self.continents = []
	
		self.cardDeck = []
		self.setValues = []
		self.tradedinSet = 0
		self.incValue = 0
		
		self.currentPhase = ""
		self.selectedTerritories = []
		self.bonusTerritories = []
		self.bonusTerritoryTraded = False
		self.conqueredNewTerritory = False
	
		self.riskInterface = riskInterface
		

	def resupplyArmies(self):
		additionalArmies = len(self.currentPlayer.ownedTerritories) / 3
		if additionalArmies < 3: 
			additionalArmies = 3
		for continent in self.currentPlayer.ownedContinents:
			additionalArmies += continent.armiesValue
		self.currentPlayer.ownedArmies += additionalArmies


	def tradeinCards(self, cardSet):
		if turnedinSet < len(self.setValues):
			additionalArmies = self.setValues[self.turnedinSet]
		else:
			additionalArmies = self.setValues[-1] + incValue * (tradedinSet - len(self.setValues) + 1)
		self.tradedinSet += 1
		self.currentPlayer.ownedArmies += additionalArmies
		
		for card in cardSet:
			self.currentPlayer.ownedCards.remove(card)
			
	
	def placeArmies(territory, armies = 1):
		if territory.owner is None:
			territory.owner = self.currentPlayer
			self.currentPlayer.ownedTerritories.append(territory)
		
		territory.armies += armies
		self.currentPlayer.ownedArmies -= armies
	
	
	def attack(baseTerritory, enemyTerritory, attackDice, defendDice):
		while len(attackDice) > 0 and len(defendDice) > 0:
			if attackDice.pop() > defendDice.pop():
				enemyTerritory.armies -= 1
			else:
				baseTerritory.armies -= 1	
	
		if enemyTerritory.armies == 0:
			return 1
		else:
			return 0
		
		
	def drawCard(self):
		if len(self.cardDeck) > 0:
			self.currentPlayer.ownedCards.append(cardDeck.pop())
		
	
	def moveArmies(self, fromTerritory, toTerritory, armies):
		fromTerritory.armies -= armies
		toTerritory.armies += armies
			
	"""------------------------------------"""

	def addPlayer(self, playerName):
		p = Player(playerName)
		self.playerList.append(p)
		
		
	def nextPlayer(self):
		self.currentPlayer = self.playerList[(self.playerList.index(self.currentPlayer) + 1) % len(self.playerList)]
	
	
	def eliminatePlayer(self, player):
		self.currentPlayer.ownedCards.extend(player.ownedCards)
		
	"""------------------------------------"""	
		
	def setupPhase(self):
		for player in self.playerList:
			player.ownedArmies = 50 - 5 * len(self.playerList)
		
		random.shuffle(self.playerList)
		self.currentPlayer = self.playerList[0]
		
	
	def setupPhasePlaceArmies(self, territory):	
		freeTerritoryList = [t for t in territories.values() if t.owner is None]
		if (freeTerritoryList and not territory.owner is None) or (not freeTerritoryList and not territory.owner is self.currentPlayer):
			return
		self.placeArmies(territory)
		self.nextPlayer()
		if self.currentPlayer.ownedArmies == 0:
			self.setupPhaseEnd()	
	
	
	def setupPhaseEnd(self):			
		self.currentPlayer = self.playerList[0]
			
	"""---------Positioning phase----------"""	
	
	def positioningPhase(self):
		self.resupplyArmies()
		if len(self.currentPlayer.ownedCards) >= 5:
			self.riskInterface.selectCardSet()
	
		
	def positioningPhaseCardsSelected(self, cardSet):		
		ownedCardTerritories = [c.territory for c in cardSet if c.territory in self.currentPlayer.ownedTerritories]
				
		self.tradeinCards(cardSet)	
		if len(ownedCardTerritories) > 0 and not self.bonusTerritoryTraded:
			if len(ownedCardTerritories) == 1:
				self.currentPlayer.ownedArmies += 2
				self.placeArmies(ownedCardTerritories[0], 2)
				self.bonusTerritoryTraded = True
				if len(self.currentPlayer.ownedCards) >= 5:
					self.riskInterface.selectCardSet()
			else:
				for territory in ownedCardTerritories:
					self.riskInterface.highlightTerritory(territory)
				self.bonusTerritories = ownedCardTerritories
		elif len(self.currentPlayer.ownedCards) >= 5:
			self.riskInterface.selectCardSet()
	
			
	def positioningPhaseTerritorySelected(self, territory):		 
		if len(self.bonusTerritories) > 0:
			if territory in bonusTerritories:
				self.currentPlayer.ownedArmies += 2
				self.placeArmies(territory, 2)
				self.bonusTerritoryTraded = True
				for bonusTerritory in bonusTerritories:
					self.riskInterface.unhighlightTerritory(bonusTerritory)
				del self.bonusTerritories
				if len(self.currentPlayer.ownedCards) >= 5:
					self.riskInterface.selectCardSet()
		else:
			self.placeArmies(territory)
			if self.currentPlayer.armies == 0:
				self.nextPhase()
	
	
	def positioningPhaseEnd(self):
		pass

	"""----------Attacking phase-----------"""
	
	def attackingPhase(self):		
		pass
		
		
	def attackingPhaseTerritorySelected(self, territory):
		if len(self.selectedTerritories) == 0 and territory.owner is self.currentPlayer and territory.armies > 1:
			selectedTerritories.append(territory)
		elif len(self.selectedTerritories) == 1 and not territory.owner is self.currentPlayer and self.selectedTerritories[0].isNeighbour(territory):
			selectedTerritories.append(territory)
			maxAttackArmies = min(self.selectedTerritories[0].armies - 1, 3)
			maxDefendArmies = min(self.selectedTerritories[1].armies, 2)
			self.riskInterface.selectDice(maxAttackArmies, maxDefendArmies)
			
			
	def attackingPhaseRollDice(attackArmies, defendArmies):
		attackDice = [random.randint(1, 6) for i in range(attackArmies)]
		attackDice.sort()
		attactDice.reverse()	
	
		defendDice = [random.randint(1, 6) for i in range(defendArmies)]
		defendDice.sort()
		defendDice.reverse()
		
		return [attackDice, defendDice]
			
		
	def attackingPhasePerformBattle(self, attackArmies, defendArmies):
		[attackDice, defendDice] = self.attackingPhaseBattleDice(attackArmies, defendArmies)
		result = self.attack(self.selectedTerritory[0], self.selectedTerritory[1], attackDice, defendDice)
		
		if result == 0: 
			maxAttackArmies = min(self.selectedTerritories[0].armies - 1, 3)
			maxDefendArmies = min(self.selectedTerritories[1].armies, 2)
			if MaxAttackArmies > 0:
				self.riskInterface.selectDice(maxAttackArmies, maxDefendArmies)
		else:
			enemyPlayer = self.selectedTerritories[1].owner
			enemyPlayer.ownedTerritories.remove(self.selectedTerritories[1])
			if len(enemyPlayer.ownedTerritories) == 0:
				self.eliminatePlayer(enemyPlayer)
			
			self.selectedTerritories[1].owner = self.currentPlayer
			self.conqueredNewTerritory = True
			minMoveArmies = min(attackArmies, self.selectedTerritories[0].armies - 1)
			maxMoveArmies = self.selectedTerritories[0].armies - 1
			if minMoveArmies == maxMoveArmies:
				self.moveArmies(self.selectedTerritories[0], self.selectedTerritories[1], maxMoveArmies)
			else:
				self.riskInterface.moveArmies(minMoveArmies, maxMoveArmies)
	
			
	def attackingPhaseEndBattle(self):
		del self.selectedTerritories
		
		if len(self.currentPlayer.ownedCards) >= 6:
			self.riskInterface.selectCardSet()
		
	
	def attackingPhaseEnd(self):
		if self.conqueredNewTerritory:
			self.drawCard()	
	
	"""----------Fortifying phase----------"""
	
	def fortifyingPhase(self):
		pass
		
		
	def foritfyingPhaseTerritorySelected(self, territory):
		if len(self.selectedTerritories) == 0 and territory.owner is self.currentPlayer and territory.armies > 1:
			selectedTerritories.append(territory)
		elif len(self.selectedTerritories) == 1 and territory.owner is self.currentPlayer and self.selectedTerritories[0].isNeighbour(territory):
			selectedTerritories.append(territory)
			maxMoveArmies = self.selectedTerritories[0].armies - 1
			self.riskInterface.moveArmies(1, maxMoveArmies)
			
			
	def fortifyingPhaseEnd(self):
		pass
		
	"""------------------------------------"""
	
	def nextPhase():
		if self.currentPhase == "Setup":
			self.setupPhaseEnd()
			self.currentPhase = "Positioning"
		elif self.currentPhase == "Positioning":
			self.positioningPhaseEnd()
			self.currentPhase = "Attacking"
		elif currentPhase == "Attacking":
			self.attackingPhaseEnd()
			self.currentPhase = "Fortifying"
		elif self.currentPhase == "Fortifying":
			self.fortifyingPhaseEnd()
			self.currentPhase = "Positioning"
			self.nextTurn()

		
	def territorySelected(self, territory):
		if self.currentPhase == "Setup":
			self.setupPlaceArmies(territory)
		elif self.currentPhase == "Positioning":
			self.positioningPhaseTerritorySelected(territory)
		elif self.currentPhase == "Attacking":
			self.attackingPhaseTerritorySelected(territory)
		elif self.currentPhase == "Fortifying":
			self.fortifyingPhaseTerritorySelected(territory)


	def movingArmiesSelected(self, armies):
		self.moveArmies(self.selectedTerritory[0], self.selectedTerritory[1], armies)
		if currentPhase == "Fortifying":
			self.nextPhase()

		
	def cardSetSelected(self, cardSet):
		self.positioningPhaseCardsSelected(cardSet)

