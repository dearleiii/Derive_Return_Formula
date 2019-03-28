import re
from z3 import *
import operator
import sys

def get_z3_object(obj_str, x, y, z):
    """
    Convert the string type variable into z3 variable
    """
    try:
        int(obj_str)
        # is_num = True
        return int(obj_str)
    except ValueError:
        # is_num = False
        return {
            "x": x,
            "y": y,
            "z": z,
        }[obj_str]

def get_if_operator(op):
    """
    Convert the if condition operators (dtype: string) into python operator
    """
    return {
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
    }[op]

def get_operator_fn(op):
    """
    Convert general operators (dtype: string) into python operator
    """
    return {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '//' : operator.floordiv,
        '/' : operator.truediv,
        '%' : operator.mod,
        '+=': operator.iadd,
        '-=': operator.isub,
        '*=': operator.imul,
        '/=': operator.itruediv,
        '//=': operator.ifloordiv,
        '%=': operator.imod,
        '^' : operator.xor,
    }[op]

def def_handler():
    """
    Initialize z3 operator
    :return:
    """
    x = Int('x')
    y = Int('y')
    z = x

    return x, y, z

def return_handler(x, y, z, word_list):
    # when no operation required but return directly
    if len(word_list) == 1:
        result = get_z3_object(word_list[0], x, y, z)

        return result

    # general case for len(word_list)
    if len(word_list) % 2 == 0:
        print("Not a valid formula\n")
        sys.exit(0)
    else:
        left_op = get_z3_object(word_list[0], x, y, z)
        for i in range(0, len(word_list)-2, 2):
            right_op = get_z3_object(word_list[i + 2], x, y, z)
            result = get_operator_fn(word_list[i + 1])(left_op, right_op)
            left_op = result

    return simplify(result)

def get_if_blocks(line_if_idx, content):
    regex = re.compile(r'^(?P<indent>(?: {4})*)(?P<name>\S.*)')
    match = regex.match(content[line_if_idx])
    if_level = len(match.group('indent')) // 4

    block1 = []
    block2 = []
    else_switch = False
    block_switch = False

    # assign level to each line
    for line_idx, line in enumerate(content[line_if_idx+1:]):
        if not line.strip():
            # this is for skip empty line
            continue

        match = regex.match(line)
        if not match:
            raise ValueError(
                'Indentation not a multiple of 4 spaces: "{0}"'.format(line)
            )
        curr_level = len(match.group('indent')) // 4

        if not else_switch:
            # No 'else' in this if statement
            if curr_level >= (if_level + 1) and not block_switch:
                block1.append(line_if_idx + line_idx + 1)
            else:
                # switch to the second block of 'if' statement
                block_switch = True
                if line.split()[0] == "else":
                    else_switch = True
                    continue
                block2.append(line_if_idx + line_idx + 1)
        else:
            if curr_level == (if_level + 1):
                block2.append(line_if_idx + line_idx + 1)
            else:
                break
    print("if block1:{} | block2:{}".format(block1, block2))
    return block1, block2


def get_block_result(content, block, x, y, z):
    """
    Block structure might contain >= 1 lines of types: If line/ return line/ z3 line
    :param block:
        block represented by line indexes, dtype: list
    :param content:
        content represented by lines of the whole original function, dtype: list
    :return:
        formula value, dtype: simplified z3 formula
    """
    for line_idx in block:
        line = content[line_idx]
        word_list = list(filter(None, re.split("[: ]" ,line)))
        line_type = word_list.pop(0)

        if line_type == "return":
            block_output = return_handler(x, y, z, word_list)
            return block_output
        elif line_type == "if":
            # print("block if line: ", word_list)
            block1, block2 = get_if_blocks(line_idx, content)

            if_step = if_handler(x, y, z, content, word_list, block1, block2)
            # print("passed in from if_step():", if_step)
            # jump to outside if blocks
            block_output = if_step
            break;
        else:
            obj_target = z3_handler(line_type, x, y, z, word_list)
            if line_type == 'x':
                x = obj_target
                block_output = x
            elif line_type == 'y':
                y = obj_target
                block_output = y
            elif line_type == 'z':
                z = obj_target
                block_output = z
            else:
                print("Please assign to the correct value among x, y, z.")
                sys.exit(0)

    return simplify(block_output)


def if_handler(x, y, z, content, word_list, block1, block2):
    left_op = get_z3_object(word_list[0], x, y, z)
    right_op = get_z3_object(word_list[2], x, y, z)
    condition = get_if_operator(word_list[1])(left_op, right_op)

    z3_st1 = get_block_result(content, block1, x, y, z)
    z3_st2 = get_block_result(content, block2, x, y, z)

    if_step = If(condition, z3_st1, z3_st2)

    return simplify(if_step)


def z3_handler(obj_target, x, y, z, word_list):
    obj_target = get_z3_object(obj_target, x, y, z)
    assign_op = word_list.pop(0)
    if assign_op == '=':
        # compute right formula first, then assign
        if len(word_list) == 1:
            obj_target = get_z3_object(word_list[0], x, y, z)

            return obj_target

        # general case for len(word_list)
        if len(word_list) % 2 == 0:
            print("Not a valid formula\n")
            sys.exit(0)
        else:
            left_op = get_z3_object(word_list[0], x, y, z)
            for i in range(0, len(word_list) - 2, 2):
                right_op = get_z3_object(word_list[i + 2], x, y, z)
                result = get_operator_fn(word_list[i + 1])(left_op, right_op)
                left_op = result

        return simplify(result)

    else:
        # directly assign for operation +=, -= , *= ect.
        right_op = get_z3_object(word_list[0], x, y, z)
        obj_target = get_operator_fn(assign_op)(obj_target, right_op)

        return obj_target