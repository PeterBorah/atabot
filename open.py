import re
from sys import argv

def create_blank(x, y):
    board = {}
    board["x_size"] = x
    board["y_size"] = y
    for j in range(y):
        board[j] = {}
        for i in range(x):
            board[j][i] = False
            
    return board

def interpret_rle(rle, board):
    try:
        row_num = 1
        column_num = 1
        char_num = 0
        while char_num < len(rle):
            char = rle[char_num]
            if char == "b":
                column_num += 1
            elif char == "o":
                board[row_num][column_num] = True
                column_num += 1
            elif char == "$":
                column_num = 1
                row_num += 1
            elif char == "!":
                break
            else:
                repeat = re.match('\d+', rle[char_num:])
                repeat_num = int(repeat.group())
                next = rle[repeat.end() + char_num]
                char_num += repeat.end()
                
                if next == "b":
                    column_num += repeat_num
                elif next == "o":
                    for i in range(repeat_num):
                        board[row_num][column_num] = True
                        column_num += 1
                elif next == "$":
                   row_num += repeat_num
                   column_num = 1
                   
                   
            char_num += 1
    except:
        print "Bad RLE file, or bad RLE interpreter."
    return board

def open_rle(file):
    f = open(file)
    rle = ""
    try:
        for line in f:
            if line[0] == 'x':
                x_begin = re.search('x\s*=\s*', line)
                x_end = line.find("," , x_begin.end())
                x_size = int(line[x_begin.end():x_end])
                y_begin = re.search('y\s*=\s*', line)
                y_end = line.find("," , y_begin.end())
                y_size = int(line[y_begin.end():y_end])

            elif line[0] == '#':
                pass
            
            else:
                rle += line[:-1]
        
        board = create_blank(x_size + 2, y_size + 2)
        return interpret_rle(rle, board)
                    
    except:
        print "Bad RLE file, or bad RLE opener."
        
def print_board(board):
    for j in range(board["y_size"]):
        row_result = ""
        for i in range(board["x_size"]):
            if board[j][i] == True:
                row_result += "X"
            else:
                row_result += "O"
        print row_result
        
def export(board):
    rle = "x = %d, y = %d\n" % (board["x_size"], board["y_size"])
    for j in range(board["y_size"]):
        for i in range(board["x_size"]):
            if board[j][i] == True:
                rle += "o"
            else:
                rle += "b"
        rle += "$"
    rle = rle[0:-1] + "!"
    return rle