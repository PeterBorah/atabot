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

def time_it(x, y, algorithm, iterations, a = None, b = None):
    max_time = datetime.timedelta(0)
    min_time = datetime.timedelta(days = 1)
    total_time = datetime.timedelta(0)
    total_steps = 0
    failed = 0
    for i in range(iterations):
        board = random_pattern(x, y)
        start = datetime.datetime.now()
        if algorithm == breakout or algorithm == breakout_bail:
            game_obj = game.Breakout(board)
        else:
            game_obj = game.Hillclimber(board)
        if b: 
            res = algorithm(game_obj, a, b)
        elif a: 
            res = algorithm(game_obj, a)
        else:
            res = algorithm(game_obj)
        if res:
            time = (datetime.datetime.now()-start)
            if time > max_time: max_time = time
            if time < min_time: min_time = time
            total_time += time
            total_steps += res
        else: 
            failed += 1
    return total_steps/(iterations - failed), total_time/(iterations - failed), min_time, max_time, failed
    
def jittery_simple(game_obj):
    while game_obj.total_needy > 0:
        game_obj.use_hc()
        
def jittery_steep(game_obj, n, timeout=1):
    start = datetime.datetime.now()
    i = 0
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        game_obj.use_sahc(n)
    return i
    
def steep_bail(game_obj, n, timeout=1):
    start = datetime.datetime.now()
    step_start = start
    i = 0
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        step_time = datetime.datetime.now() - step_start
        if step_time > datetime.timedelta(seconds = 10):
            board = game_obj.board
            game_obj = game.Hillclimber(board, random=True)
            step_start = datetime.datetime.now()
        game_obj.use_sahc(n)
    return i
    
def test_algo(game_obj, n, timeout = 1):
    start = datetime.datetime.now()
    i = 0
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        game_obj.use_test_algo(n)
    return i
    
def pogo(game_obj, timeout = 1):
    start = datetime.datetime.now()
    i = 0
    step_start = start
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        game_obj.use_pogo()
    return i
    
def pogo_bail(game_obj, timeout = 1):
    start = datetime.datetime.now()
    i = 0
    step_start = start
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        step_time = datetime.datetime.now() - step_start
        if step_time > datetime.timedelta(seconds = 10):
            board = game_obj.board
            game_obj = game.Hillclimber(board, random=True)
            step_start = datetime.datetime.now()
        game_obj.use_pogo()
    return i
    
def breakout_bail(game_obj, timeout=1):
    start = datetime.datetime.now()
    i = 0
    step_start = start
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        step_time = datetime.datetime.now() - step_start
        if step_time > datetime.timedelta(seconds = 10):
            board = game_obj.board
            game_obj = game.Breakout(board, random=True)
            step_start = datetime.datetime.now()
        game_obj.use_breakout()
    return i
    
def breakout(game_obj, timeout=1):
    start = datetime.datetime.now()
    i = 0
    while game_obj.total_needy > 0:
        i += 1
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        game_obj.use_breakout()
    return i
    
def combo(game_obj, a, b, timeout=1):
    start = datetime.datetime.now()
    while game_obj.total_needy > 0:
        time = datetime.datetime.now() - start
        if time > datetime.timedelta(minutes = timeout):
            return False
        game_obj.use_combo(a, b)
    return True
    
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
    
def compare_test_algos(x, y, iterations, timeout = 30):
    x, y, iterations = int(x), int(y), int(iterations)

    steps, avg, min, max, failed = time_it(x, y, jittery_steep, iterations, 2)
    print "Steep   2: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, jittery_steep, iterations, 3)
    print "Steep   3: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, jittery_steep, iterations, 4)
    print "Steep   4: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, test_algo, iterations, 2)
    print "Test    2: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, test_algo, iterations, 3)
    print "Test    3: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, test_algo, iterations, 4)
    print "Test    4: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    
def compare_combos(x, y, iterations):
    x, y, iterations = int(x), int(y), int(iterations)
    
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 2, 2)
    print "Combo 2 2: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 2, 3)
    print "Combo 2 3: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 2, 4)
    print "Combo 2 4: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 3, 2)
    print "Combo 3 2: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 3, 3)
    print "Combo 3 3: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 3, 4)
    print "Combo 3 4: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 4, 2)
    print "Combo 4 2: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 4, 3)
    print "Combo 4 3: %s, %s, %s, %s" % (avg, min, max, failed)
    steps, avg, min, max, failed = time_it(x, y, combo, iterations, 4, 4)
    print "Combo 4 4: %s, %s, %s, %s" % (avg, min, max, failed)
 
def compare_bail(x, y, iterations, timeout=1): 
    print "%sx%s, %s iterations, %sm timeout" % (x, y, iterations, timeout)
    steps, avg, min, max, failed = time_it(x, y, breakout_bail, iterations, timeout)    
    print "brkout bl: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, pogo, iterations)
    print "pogo     : %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, pogo_bail, iterations, timeout)
    print "bail pogo: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, jittery_steep, iterations, 3, timeout)
    print "steep   3: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    steps, avg, min, max, failed = time_it(x, y, steep_bail, iterations, 3, timeout)
    print "bail stp3: %s, %s, %s, %s, %s" % (avg, min, max, failed, steps)
    
if __name__ == '__main__':
    compare_bail(5, 5, 1000)
    