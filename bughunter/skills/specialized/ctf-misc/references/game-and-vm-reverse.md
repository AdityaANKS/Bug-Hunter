# Games and customization VM Reverse

## Brainfuck

```python
# Brainfuck interpreter
import sys

def brainfuck(code, input_data=''):
    code = ''.join(c for c in code if c in '><+-.,[]')
    tape = [0] * 30000
    ptr = 0
    iptr = 0
    input_ptr = 0
    output = []

    while iptr < len(code):
        op = code[iptr]
        if op == '>':
            ptr += 1
        elif op == '<':
            ptr -= 1
        elif op == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif op == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif op == '.':
            output.append(chr(tape[ptr]))
        elif op == ',':
            if input_ptr < len(input_data):
                tape[ptr] = ord(input_data[input_ptr])
                input_ptr += 1
            else:
                tape[ptr] = 0
        elif op == '[':
            if tape[ptr] == 0:
                depth = 1
                while depth > 0:
                    iptr += 1
                    if code[iptr] == '[':
                        depth += 1
                    elif code[iptr] == ']':
                        depth -= 1
        elif op == ']':
            if tape[ptr] != 0:
                depth = 1
                while depth > 0:
                    iptr -= 1
                    if code[iptr] == '[':
                        depth -= 1
                    elif code[iptr] == ']':
                        depth += 1
        iptr += 1

    return ''.join(output)
```

## Ook!

```python
# Ook! arrive Brainfuck Convert
ook_to_bf = {
    'Ook. Ook?': '>',
    'Ook? Ook.': '<',
    'Ook. Ook.': '+',
    'Ook! Ook!': '-',
    'Ook! Ook.': '.',
    'Ook. Ook!': ',',
    'Ook! Ook?': '[',
    'Ook? Ook!': ']',
}
```

## Customize VMReverse process

```python
# Analysis customization VM Steps:
# 1. turn up opcode definition table
# 2. turn up VM Initialization code (register、memory initialization)
# 3. track main loop, find the instruction distribution
# 4. Analyze each opcode Function
# 5. Extract bytecode File
# 6. Write disassembler or directly simulate execution

"""
Common opcode Mode:
0x00 = NOP
0x01 = LOAD  (Load data)
0x02 = STORE (Store Data)
0x03 = ADD
0x04 = SUB
0x05 = JMP
0x06 = JZ    (Conditional jump)
0x07 = HALT
"""

class SimpleVM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.regs = [0] * 8
        self.memory = bytecode[256:]  # Assume data follows code
        self.pc = 0
        self.running = True

    def step(self):
        op = self.bytecode[self.pc]
        if op == 0x01:  # LOAD
            self.pc += 1
            reg = self.bytecode[self.pc]
            self.pc += 1
            addr = self.bytecode[self.pc]
            self.regs[reg] = self.memory[addr]
        elif op == 0x05:  # JMP
            self.pc += 1
            self.pc = self.bytecode[self.pc]
        elif op == 0x07:  # HALT
            self.running = False
        self.pc += 1

    def run(self):
        while self.running and self.pc < len(self.bytecode):
            self.step()
```

## Z3 Constraint solving

```python
from z3 import *

def solve_with_z3(constraints, variables):
    """Use Z3 Solve constraints"""
    s = Solver()
    for constraint in constraints:
        s.add(constraint)
    if s.check() == sat:
        model = s.model()
        return {v: model[v] for v in variables}
    return None
```

## WASM Analysis

```python
# Commonly Used wasm Analysis command
"""
# Extract wasm String
strings game.wasm | grep -i flag

# View Export Functions
wasm-objdump -h game.wasm

# Decompiled to wasm Text format
wasm2wat game.wasm -o game.wat

# View function
wasm-objdump -d game.wasm

# Use wasmer Or wasmtime Execute
wasmer game.wasm
"""
```
