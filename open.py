import re
from sys import argv

def initialize_board(x, y):
    board = {}
    for i in range(x):
        for j in range(y):
            board[str(i)+str(j)] = False
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
                board[str(column_num) + str(row_num)] = True
                column_num += 1
            elif char == "$":
                column_num = 0
                break
            elif char == "!":
                return board
            else:
                repeat = re.match('\d+', row[char_num:])
                repeat_num = int(repeat.group())
                next = row[repeat.end() + char_num]
                char_num += repeat.end()
                if next == "b":
                    column_num += repeat_num
                elif next == "o":
                    for i in range(repeat_num):
                        board[str(column_num) + str(row_num)] = True
                        column_num += 1
                elif next == "$":
                   row_num += repeat_num - 1
                   column_num = 0
                   break
                   
            char_num += 1        
                
        row_num += 1
    return board

def open_rle(file):
    rle = open(file)
    rows = []
    try:
        for line in rle:
            if line[0] == 'x':
                x_param = re.search('x\s*=\s*(\d)*', line)
                x_param = int(x_param.group(1))
                y_param = re.search('y\s*=\s*(\d)*', line)
                y_param = int(y_param.group(1))

            elif line[0] == '#':
                pass
            
            else:
                while line:
                    row = re.match('[^$!]+[$!]', line)
                    line = line[row.end():]
                    row = row.group()
                    rows.append(row)
        
        board = initialize_board(x_param, y_param)
        return board_create(rows, x_param, board)
                    
    except:
        print "Bad RLE file, or bad RLE interpreter."
        
print open_rle(argv[1])