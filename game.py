import random
from sys import argv

import open

class Game(object):
    def __init__(self, board):
        self.board = board
        self.candidate = open.create_blank(board["x_size"], board["y_size"])
        self.needy = self.initialize_neediness()
        self.impact = self.initialize_impact()
        
    def get_neighborhood(self, cell):
        x = cell[0]
        y = cell[1]
        result = []
        if x == 0:
            x_range = [0, 1]
        elif x == self.board["x_size"] - 1:
            x_range = [self.board["x_size"] - 2, self.board["x_size"] - 1]
        else:
            x_range = [x - 1, x, x+1]
            
        if y == 0:
            y_range = [0, 1]
        elif y == self.board["y_size"] - 1:
            y_range = [self.board["y_size"] - 2, self.board["y_size"] - 1]
        else:
            y_range = [y - 1, y, y + 1]
            
        for i in x_range:
            for j in y_range:
                result.append((i, j))
                
        return result
        
    def get_neediness(self, cell, flipped=False):
        x = cell[0]
        y = cell[1]
        desired = self.board[y][x]
        if flipped == cell:
            state = not self.candidate[y][x]
        else:
            state = self.candidate[y][x]
            
        neighbor_count = 0
        neighborhood = self.get_neighborhood(cell)
        neighborhood.remove(cell)
        for neighbor in neighborhood:
            if flipped == neighbor:
                if self.candidate[neighbor[1]][neighbor[0]] == False:
                    neighbor_count += 1 
            else:
                if self.candidate[neighbor[1]][neighbor[0]] == True:
                    neighbor_count += 1
                
        if state == True and desired == True:
            if neighbor_count < 2:
                return 2 - neighbor_count
            elif neighbor_count > 3:
                return neighbor_count - 3
            else:
                return 0
        elif state == True and desired == False:
            if neighbor_count == 2 or neighbor_count == 3:
                return 1
            else:
                return 0
                
        elif state == False and desired == False:
            if neighbor_count == 3:
                return 1
            else:
                return 0
                
        else:
            if neighbor_count > 3:
                return neighbor_count - 3
            elif neighbor_count < 3:
                return 3 - neighbor_count
            else:
                return 0
                
    def get_impact(self, cell):
        neighborhood = self.get_neighborhood(cell)
        total = 0
        for neighbor in neighborhood:
            new = self.get_neediness(neighbor, cell)
            change = self.needy[neighbor[1]][neighbor[0]] - new
            total += change
        return total
    
    def initialize_neediness(self):
        needy = {}
        x = self.board["x_size"]
        y = self.board["y_size"] 
        self.total_needy = 0
        for j in range(y):
            needy[j] = {}
            for i in range(x):
                score = self.get_neediness((i,j))
                needy[j][i] = score
                self.total_needy += score
        return needy
        
    def initialize_impact(self):
        impact = {}
        x = self.board["x_size"]
        y = self.board["y_size"] 
        for j in range(y):
            impact[j] = {}
            for i in range(x):
                impact[j][i] = self.get_impact((i,j))
        return impact
        
    def get_big_neighborhood(self, cell): #inelegant as beans
        small = self.get_neighborhood(cell)
        big = []
        for neighbor in small:
            big += self.get_neighborhood(neighbor)
        big = set(big)
        return big
        
    def update_impact(self, cell):
        affected = self.get_big_neighborhood(cell)
        for place in affected:
            x = place[0]
            y = place[1]
            self.impact[y][x] = self.get_impact((x,y))
            
    def update_neediness(self, cell):
        x = cell[0]
        y = cell[1]
        neighborhood = self.get_neighborhood(cell)
        for neighbor in neighborhood:
            self.needy[neighbor[1]][neighbor[0]] = self.get_neediness(neighbor)
            
    def use_jhc(self, chance = 3):
        '''Jittery Hill-Climbing algorithm'''
        
        if random.choice(range(chance)) == 0:
            flip_cell = (random.choice(range(self.board["x_size"])),
                        random.choice(range(self.board["y_size"])))
        else:
            best_score = self.impact[0][0]
            best_list = []
            for j in range(self.board["y_size"]):
                for i in range(self.board["x_size"]):
                    score = self.impact[j][i]
                    if score > best_score:
                        best_score = score
                        best_list = [(i, j)]
                    elif score == best_score:
                        best_list.append((i, j))
            flip_cell = random.choice(best_list)
            
        x = flip_cell[0]
        y = flip_cell[1]
        self.candidate[y][x] = not self.candidate[y][x]
        self.total_needy -= self.impact[y][x]
        self.update_neediness(flip_cell)
        self.update_impact(flip_cell)

board = open.open_rle(argv[1])        
test = Game(board)
i = 0
while test.total_needy > 0:
    test.use_jhc()
    print test.total_needy
    i += 1
print open.export(test.candidate)
print i