"""
    This python program will automatically derives the return value formula,
with given python source code in string format.
    Input constrains:
    - Pure python functions that takes 2 integers x, y and return 1 integer;
    - Input function does not have function calls/ imports/ loops/ exceptions
    - Input function only have integer local variables

    Output:
    - A z3 expression

    Created by @ Lei Chen
"""
import z3
from z3 import *
from os.path import join, isfile
# from helper import *
from blocks import *
import sys
import re

test_dir = "/Users/dearleiii/Desktop/2019Duke/OA/Z3/"
test_file = "input6.txt"

if not isfile(join(test_dir, test_file)):
    print("File does not exist.")

with open(join(test_dir, test_file)) as f:
    content = f.read().splitlines()
    for line_idx, line in enumerate(content):
        # word_list = line.split()       # split each line on: ' ' only
        word_list = list(filter(None, re.split("[: ]" ,line)))
        line_type = word_list.pop(0)

        if line_type == "def":
            x, y, z = def_handler()
        elif line_type == "return":
            # print("return line:", word_list)
            output = return_handler(x, y, z, word_list)
            break;  # no need for further lines?
        elif line_type == "if":
            #print("handle if line: ", word_list)
            block1, block2 = get_if_blocks(line_idx, content)
            # print("if block1 lines:{}, block 2 lines: {}".format(block1, block2))

            if_step = if_handler(x, y, z, content, word_list, block1, block2)
            # jump to outside if blocks-2
            output = if_step
            break;
        else:
            print("z3 operation line: ", word_list)
            obj_target = z3_handler(line_type, x, y, z, word_list)
            # line_type: the object need to be assign new value
            if line_type == 'x':
                x = obj_target
            elif line_type == 'y':
                y = obj_target
            elif line_type == 'z':
                z = obj_target
            else:
                print("Please assign to the correct value among x, y, z.")
                sys.exit(0)

# return z3 expression
print("Output return value formula: \n", output)
