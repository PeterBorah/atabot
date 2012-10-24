import random
import tools

class Search(object):

    '''Contains all the basic code for running a local search for predecessors.

    When you instantiate the class, you must pass it a GoL board in the form
    of a nested dictionary. There are two key methods, "use_jittery()" and 
    "use_pogo()", each of which runs one step of one of the two algorithms 
    currently implemented. Everything else is in the service of one or (usually)
    both of those methods.

    '''
    
    def __init__(self, board):
    
        '''Create the basic objects needed for the search.
        
        self.board is the target board, self.candidate is the current candidate
        to be tested and modified, self.needy is a matrix of how bad a shape each 
        cell is in, self.total_needy is a sum of the values of self.needy, and 
        self.impact is a matrix of how beneficial flipping each cell would be. 
        
        self.minima is used to store known minima for the Pogo algorithm. It is 
        initialized here mostly so I don't have to check for it every time I run 
        use_pogo().
        
        '''
    
        self.board = board
        self.candidate = tools.create_random(board["x_size"], 
                                                 board["y_size"])
        self.candidate = tools.create_blank(board["x_size"], 
                                                 board["y_size"])
        self.needy, self.total_needy = self.initialize_neediness()
        self.impact = self.initialize_impact()
        self.minima = {}
        
    def get_neighborhood(self, cell):
        '''Return every cell in the neighborhood of the target cell.'''
    
        x = cell[0]
        y = cell[1]
        result = []
        if x == -1:
            x_range = [-1, 0]
        elif x == self.board["x_size"]:
            x_range = [self.board["x_size"] - 1, self.board["x_size"]]
        else:
            x_range = [x - 1, x, x+1]
            
        if y == -1:
            y_range = [-1, 0]
        elif y == self.board["y_size"]:
            y_range = [self.board["y_size"] - 1, self.board["y_size"]]
        else:
            y_range = [y - 1, y, y + 1]
            
        for i in x_range:
            for j in y_range:
                if (i, j) != cell:
                    result.append((i, j))
                
        return result
        
    def get_big_neighborhood(self, cell):
        '''Return every cell within distance 2 of the passed cell.
        
        Currently does this by calling self.get_neighborhood() on each cell in the 
        cell's neighborhood. This should probably be replaced by something more 
        elegant/efficient. Note: unlike self.get_neighborhood(), this includes the
        current cell in the result.
        
        '''
        small = self.get_neighborhood(cell)
        big = []
        for neighbor in small:
            big += self.get_neighborhood(neighbor)
        big = set(big)
        return big
        
    def get_neediness(self, cell, flipped=None):
        '''Return the distance the target cell is from the desired state
        
        This is defined as the number of neighbors in the candidate that will need 
        to change state before the target cell will have the desired behavior in the 
        next generation. The optional "flipped" argument can be used to specify a 
        cell that the method should treat as if it were in the opposite state than 
        it currently is.
        
        '''
        x = cell[0]
        y = cell[1]
        desired = self.board[y][x]
        if flipped == cell:
            state = not self.candidate[y][x]
        else:
            state = self.candidate[y][x]
            
        neighbor_count = 0
        neighborhood = self.get_neighborhood(cell)
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
        '''Return the net benefit of flipping the passed cell.'''
        neighborhood = self.get_neighborhood(cell)
        neighborhood.append(cell)
        total = 0
        for neighbor in neighborhood:
            new = self.get_neediness(neighbor, flipped=cell)
            change = self.needy[neighbor[1]][neighbor[0]] - new
            total += change
        return total
        
    def initialize_neediness(self):
        '''Call self.get_needy() on each cell and return a matrix and a total.'''
        needy = {}
        x = self.board["x_size"]
        y = self.board["y_size"] 
        total_needy = 0
        for j in range(-1, y + 1):
            needy[j] = {}
            for i in range(-1, x + 1):
                score = self.get_neediness((i,j))
                needy[j][i] = score
                total_needy += score
        return needy, total_needy
        
    def initialize_impact(self):
        '''Call self.get_impact() on each cell and return a matrix.'''
        impact = {}
        x = self.board["x_size"]
        y = self.board["y_size"] 
        for j in range(-1, y + 1):
            impact[j] = {}
            for i in range(-1, x + 1):
                impact[j][i] = self.get_impact((i,j))
        return impact
        
    def update_neediness(self, cell):
        '''Given a recently changed cell, update self.needy with the effects.'''
        x = cell[0]
        y = cell[1]
        neighborhood = self.get_neighborhood(cell)
        neighborhood.append(cell)
        for neighbor in neighborhood:
            self.needy[neighbor[1]][neighbor[0]] = self.get_neediness(neighbor)
        
    def update_impact(self, cell):
        '''Given a recently changed cell, update self.impact with the effects.'''
        affected = self.get_big_neighborhood(cell)
        for place in affected:
            x = place[0]
            y = place[1]
            self.impact[y][x] = self.get_impact((x,y))
            
    def flip(self, cell):
        '''Flip the passed cell in self.candidate, and do the necessary updates.'''
        x = cell[0]
        y = cell[1]
        self.candidate[y][x] = not self.candidate[y][x]
        self.total_needy -= self.impact[y][x]
        self.update_neediness(cell)
        self.update_impact(cell)
    
    def use_jittery(self, chance=3):
        '''Execute one step of the jittery hillclimbing algorithm
        
        This is my adaptation of the algorithm used by Paul Callahan's Random Still 
        Life Generator. (http://www.radicaleye.com/lifepage/stilledit.html)
        
        It goes through the board, looking for the cell(s) with the best impact. It 
        chooses a cell randomly from among that list to flip. Alternatively, with a 
        chance of 1 in (chance), it flips a random cell.
        
        '''
        if random.randint(1, chance) == 1:
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
        
        self.flip(flip_cell)
        
    def use_pogo(self):
        '''Execute one step of the Pogo algorithm.
        
        This is an algorithm I invented. Similar to the jittery hillclimbing
        algorithm, it looks for the cell(s) with the best impact. If no cell has a
        positive impact (which implies the search is at a local minima), it flips some 
        number of random cells instead. This number is equal to the number of times it has 
        encountered that particular minima. The idea is that it will jump "higher" 
        the more it seems to be getting stuck.
        
        '''
        
        best_score = 1
        best_list = []
        for j in range(self.board["y_size"]):
            for i in range(self.board["x_size"]):
                score = self.impact[j][i]
                if score > best_score:
                    best_score = score
                    best_list = [(i, j)]
                elif score == best_score:
                    best_list.append((i, j))

        
        if not best_list:
            current = tools.export(self.candidate) # To get an immutable key
            if current in self.minima:
                self.minima[current] += 1
            else:
                self.minima[current] = 1
            for i in range(self.minima[current]):
                flip_cell = (random.choice(range(self.board["x_size"])),
                            random.choice(range(self.board["y_size"])))
                self.flip(flip_cell)
        else:        
            flip_cell = random.choice(best_list)
            self.flip(flip_cell)
            
            
    def cleanup(self):
        for j in range(self.board["y_size"]):
            for i in range(self.board["x_size"]):
                if self.candidate[j][i] == True and self.impact[j][i] == 0:
                    self.flip((i,j))