import re
from sys import argv

def initialize_board(x, y):
    board = {}
    board["x_size"] = x
    board["y_size"] = y
    for i in range(x):
        for j in range(y):
            board["x"+str(i)+"y"+str(j)] = False
    return board

def board_create(rows, x_param, board):
    row_num = 0
    for row in rows:
        column_num = 0
        char_num = 0
        while char_num < len(row):
            char = row[char_num]
            if char == "b":
                column_num += 1
            elif char == "o":
                board["x" + str(column_num) + "y" + str(row_num)] = True
                column_num += 1
            elif char == "$":
                column_num = 0
                break
            elif char == "!":
                break
            else:
                repeat = re.match('\d+', row[char_num:])
                repeat_num = int(repeat.group())
                next = row[repeat.end() + char_num]
                char_num += repeat.end()
                if next == "b":
                    column_num += repeat_num
                elif next == "o":
                    for i in range(repeat_num):
                        board["x" + str(column_num) + "y" + str(row_num)] = True
                        column_num += 1
                elif next == "$":
                   row_num += repeat_num - 1
                   column_num = 0
                   break
                   
            char_num += 1        
                
        row_num += 1
    return board

def interpret_rle(file):
    rle = open(file)
    rows = []
    try:
        for line in rle:
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
                while line:
                    row = re.match('[^$!]+[$!]', line)
                    line = line[row.end():]
                    row = row.group()
                    rows.append(row)
        
        board = initialize_board(x_size, y_size)
        return board_create(rows, x_size, board)
                    
    except:
        print "Bad RLE file, or bad RLE interpreter."

print interpret_rle(argv[1])