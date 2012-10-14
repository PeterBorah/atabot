from datetime import datetime
from sys import argv

import game
import tools

def time_it(board, algorithm, iterations, jittery):
    start = datetime.now()
    for i in range(iterations):
        game_obj = game.Hillclimber(board, random=not jittery)
        algorithm(game_obj)
    return (datetime.now()-start)
    
def jittery_simple(game_obj):
    while game_obj.total_needy > 0:
        game_obj.use_hc()
        
def jittery_steep(game_obj):
    while game_obj.total_needy > 0:
        game_obj.use_sahc()
        
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
    #res = time_it(board, jittery_steep, iterations, True)
    #print "Jittery Steep: %s" % res
    #res = time_it(board, jittery_simple, iterations, True)
    #print "Jittery Simple: %s" % res
    res = time_it(board, repeated_steep, iterations, False)
    print "Repeated Steep: %s" % res
    res = time_it(board, repeated_simple, iterations, False)
    print "Repeated Simple: %s" % res
    

compare_hillclimbers(argv[1], int(argv[2]))    