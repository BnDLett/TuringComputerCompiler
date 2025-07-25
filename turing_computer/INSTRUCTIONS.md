# Overview
All instructions are 64 bit — the first 32 bits are used for the instruction itself, and the last 32 bits are used for 
the value of the instruction. "[value]" indicates when the instruction accepts a given value and will be used in the 
descriptions to describe or refer to the value itself.

The register "data lane" refers to the wiring that'll write data to any given register that has its flag enabled. This 
will not write any data to any register if a register flag is not specified in the instruction.

All addresses are zero-index based, excluding flags.

"*" will be used to specify the registers that an instruction supports writing to.

# Instructions
## Register
```
0b00000000000000000000000000000001
    Write to register 1.

0b00000000000000000000000000100000
    Write to register 6.

0b00000000000000000000000000******
    Available bits for register flags.

0b00000000000000000000100000******
    Copies data from one register to other registers. The register to read from is specified via the register flag in 
    register 6. The register to write to is specified via the instruction's register flags.
```

## Jumps
```
0b00000000000000000000000010000000
    Jumps to a specified instruction in the program. Address is specified via register 1.

0b00000000000000000000000001000000
    Jumps to the top of the instruction stack

0b00000000000000000100000000000000
    Jumps if the least significant bit of register 2 is true. Instruction address is specified via register 1.
```


## Memory
```
0b00000000000000000000000100000000
    Write register 1 to RAM at 24 bit address specified in register 2

0b00000000000000000000010000******
    Reads from RAM and sends the data to the register data lane.
```


## Binary
```
0b00000000000000000010000000******
    Shifts register 1 left and sends it to the register data lane.

0b00000000000000000011000000******
    Shifts register 1 right and sends it to the register data lane.
```


# Arithmetic
```
0b00000000000000000100000000******
    Adds register 2 to register 1. If the least significant bit of register 3 is 1, then it'll subtract register 1 from 
    register 2. The result of the operation is sent to the register data lane.
```

## Unused Instructions
```
- 0b00000000000000000000001000000000
```
