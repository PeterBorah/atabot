import datetime
from sys import argv
import random

import game
import tools

def random_pattern(x, y):
    board = {}
    board["x_size"] = x + 2
    board["y_size"] = y + 2
    for j in range(y + 2):
        board[j] = {}
        for i in range(x + 2):
            board[j][i] = False
            
    for j in range(1, y + 1):
        for i in range(1, x + 1):
            board[j][i] = random.choice([True, False])
            
    return board

def time_it(x, y, algorithm, iterations, a, b = None):
    max_time = datetime.timedelta(0)
    min_time = datetime.timedelta(days = 1)
    total_time = datetime.timedelta(0)
    for i in range(iterations):
        board = random_pattern(x, y)
        start = datetime.datetime.now()
        game_obj = game.Hillclimber(board)
        if b: algorithm(game_obj, a, b)
        else: algorithm(game_obj, a)
        time = (datetime.datetime.now()-start)
        if time > max_time: max_time = time
        if time < min_time: min_time = time
        total_time += time
    return total_time/iterations, min_time, max_time
    
def jittery_simple(game_obj):
    while game_obj.total_needy > 0:
        game_obj.use_hc()
        
def jittery_steep(game_obj, n):
    while game_obj.total_needy > 0:
        game_obj.use_sahc(n)
        
def test_algo(game_obj, n):
    while game_obj.total_needy > 0:
        game_obj.use_test_algo(n)
        
def combo(game_obj, a, b):
    while game_obj.total_needy > 0:
        game_obj.use_combo(a, b)
        
def repeated_simple(game_obj):
    x = game_obj.board["x_size"]
    y = game_obj.board["y_size"]
    while game_obj.total_needy > 0:
        turn = game_obj.use_hc(jittery=False)
        if not turn:
            game_obj.candidate = tools.create_random(x, y)
            game_obj.initialize_neediness()
            game_obj.initialize_impact()
    
def repeated_steep(game_obj):
    x = game_obj.board["x_size"]
    y = game_obj.board["y_size"]
    while game_obj.total_needy > 0:
        turn = game_obj.use_sahc(jittery=False)
        if not turn:
            game_obj.candidate = tools.create_random(x, y)
            game_obj.initialize_neediness()
            game_obj.initialize_impact()
    
def compare_hillclimbers(file, iterations):
    board = tools.open_rle(file)
    res = time_it(board, jittery_steep, iterations, True)
    print "Jittery Steep: %s" % res
    res = time_it(board, jittery_simple, iterations, True)
    print "Jittery Simple: %s" % res
    res = time_it(board, repeated_steep, iterations, False)
    print "Repeated Steep: %s" % res
    res = time_it(board, repeated_simple, iterations, False)
    print "Repeated Simple: %s" % res
    
def compare_test_algos(x, y, iterations):
    x, y, iterations = int(x), int(y), int(iterations)

    avg, min, max = time_it(x, y, jittery_steep, iterations, 2)
    print "Steep   2: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, jittery_steep, iterations, 3)
    print "Steep   3: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, jittery_steep, iterations, 4)
    print "Steep   4: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, test_algo, iterations, 2)
    print "Test    2: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, test_algo, iterations, 3)
    print "Test    3: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, test_algo, iterations, 4)
    print "Test    4: %s, %s, %s" % (avg, min, max)
    
def compare_combos(x, y, iterations):
    x, y, iterations = int(x), int(y), int(iterations)
    
    avg, min, max = time_it(x, y, combo, iterations, 2, 2)
    print "Combo 2 2: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 2, 3)
    print "Combo 2 3: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 2, 4)
    print "Combo 2 4: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 3, 2)
    print "Combo 3 2: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 3, 3)
    print "Combo 3 3: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 3, 4)
    print "Combo 3 4: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 4, 2)
    print "Combo 4 2: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 4, 3)
    print "Combo 4 3: %s, %s, %s" % (avg, min, max)
    avg, min, max = time_it(x, y, combo, iterations, 4, 4)
    print "Combo 4 4: %s, %s, %s" % (avg, min, max)
    
if __name__ == '__main__':
    print "3x3, 1000 iterations"
    compare_test_algos(3, 3, 1000)
    compare_combos(3, 3, 1000)
    print "4x4, 500 iterations"
    compare_test_algos(4, 4, 500)
    compare_combos(4, 4, 500)
    print "5x5, 10 iterations"
    compare_test_algos(5, 5, 10)
    compare_combos(5, 5, 10)
    print "8x8, 1 iteration"
    compare_test_algos(8, 8, 1)
    compare_combos(8, 8, 1)
    print "11x11, 1 iteration"
    compare_test_algos(11, 11, 1)
    compare_combos(11, 11, 1)