class Territory(object):
	def __init__(self, name, owner, neighbours):
		self.name = name
		self.owner = owner
		self.neighbours = neighbours
		self.armies = 0
		
	def isNeighbour(self, territory):
		return territory in self.neighbours
		

class Continent(object):
	def __init__(self, name, continent, owner, unitValue):
		self.name = name
		self.continent = continent
		self.owner = owner
		self.armiesValue = armiesValue
		self.territories = []
		
		
class Card(object):
	def __init__(self, territory, army):
		self.territory = territory
		self.army = army 


class Player(object):
	def __init__(self, name):
		self.name = name
		self.ownedTerritories = []
		self.ownedContinents = []
		self.ownedCards = []
		self.ownedArmies = 0
		
	def isEliminated(self)
		return len(self.ownedTerritories) == 0
		
	
        
        
