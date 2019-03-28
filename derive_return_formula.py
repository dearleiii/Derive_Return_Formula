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

def main():
    test_dir = "./test/"
    test_file = sys.argv[1]

    if not isfile(join(test_dir, test_file)):
        print("File does not exist. Please put your test file in /test folder.\n")
        sys.exit(0)

    # open file and read the file by lines/ blocks accordingly
    with open(join(test_dir, test_file)) as f:
        content = f.read().splitlines()
        for line_idx, line in enumerate(content):
            # if start with # , skip the line

            word_list = list(filter(None, re.split("[: ]", line)))  # split each line word by word
            line_type = word_list.pop(0)

            # handle different line type: if line/ def line/ return line/ operation line
            if line_type == "def":
                x, y, z = def_handler()
            elif line_type == "return":
                output = return_handler(x, y, z, word_list)

                # exit program
                break;
            elif line_type == "if":
                # get the two operation block for if operation, else operation
                block1, block2 = get_if_blocks(line_idx, content)

                # get the output of if block
                if_step = if_handler(x, y, z, content, word_list, block1, block2)
                output = if_step

                # exit if block
                break;
            else:
                # handle the normal operation line
                obj_target = z3_handler(line_type, x, y, z, word_list)
                # find out the updated z3 object, update with assigned equation
                if line_type == 'x':
                    x = obj_target
                elif line_type == 'y':
                    y = obj_target
                elif line_type == 'z':
                    z = obj_target
                else:
                    print("Please assign to the correct value among x, y, z.")
                    sys.exit(0)

    # Print and return z3 expression
    print("Output return value formula: \n", output)

if __name__ == '__main__':
    main()
