# Derive_Return_Formula
This repo implements a python program that automatically derives the return value formula, using Microsoft z3.

For simplicity, we will only consider pure python functions that:

- Take two integers x and y , and return one integer.
- Do not have function calls, imports, loops, or exceptions.
- Only have integer local variables.


### Dependency: 
- python3
- z3 

### Usage: 
- Put your own test input file into /test folder
- `python derive_retun_formula.py your_input_file.txt` 
