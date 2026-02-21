# Turing Computer Compiler
Ok, not literally a *turing computer* compiler — but it is an assembler for a simple custom instruction set.

## Why a custom instruction set?
There is no particular reason outside of gathering practice in hardware engineering. Although, I will say that it helps
simplify and reduces the concern that I have in regard to actually developing the CPU. Is it cross compatible with
other compilers? Nah. Does that matter? Nah. At the end of the day, this should theoretically be able to do a
significant number of tasks on its own. ~~The only thing that's left to be desired by me is the ability to have 
peripherals available to the CPU. However, the likeliness of that feature coming any time soon is highly unlikely.~~
I lied, kinda. It has basic peripheral support now.

## Where can I find the files for the architecture?
The files can be found [here](turing_computer). I'd recommend reading the [README.md](turing_computer/README.md) for it
before you proceed to download the files for the architecture.

# Instructions
## Key
A definition will be referred to via a super script. For example: "RDL²" would refer to definition number 2, aka the
register data lane.
1. **rx** — A given register ranging from 1-6. Keep in mind that register 6 is **not** a general purpose register and
should not be used as such. Example usage: `r1`.
2. **Register data late** — The data lane that is used to specify the data to be written to a register. In other words,
if data is sent to the RDL, then that data will be written when a register is specified.
3. **Least significant bit** — The bit in a binary number with the least value. 

## Table
| NAME      | DESCRIPTION                                                                               | FORMAT                 |
|-----------|-------------------------------------------------------------------------------------------|------------------------|
| INSERT    | Inserts a value into the specified register.                                              | INSERT \[value] \[rx¹] |
| COPY      | Copies a value from the register specified in r6 to the register data lane.               | COPY \[rx¹]            |
| JUMP      | Unconditionally jumps to the instruction address specified via r1                         | JUMP                   |
| JIF       | Conditionally jumps to the instruction address in r1 if the LSB³ of r2 is 1.              | JIF                    |
| END       | Unconditionally jumps to the top of the instruction stack.                                | END                    |
| WRITE     | Writes r1 to r2 address in the RAM.                                                       | WRITE                  |
| LOAD      | Loads value at r2 address to the RDL².                                                    | LOAD \[rx¹]            |
| LSHIFT    | Shifts r1 left and writes the result to the RDL².                                         | LSHIFT                 |
| RSHIFT    | Shifts r1 right and writes the result to the RDL².                                        | RSHIFT                 |
| OP        | Adds r1 to r2. If the LSB³ of r3 is 1, then subtract instead. Result is sent to the RDL². | OP                     |
| PERIREAD  | Reads from a peripheral specified in r6 and writes it to the RDL².                        | PERIREAD \[rx¹]        |
| PERIWRITE | Triggers a signal to peripheral r6 that data should be written.                           | PERIWRITE              |
