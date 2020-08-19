"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Random access memory
        self.ram = [0] * 256 
        # Register
        self.reg = [0] * 8
        # Program counter
        self.pc = 0

        self.branch_table = {
            # Load
            LDI: self.handle_ldi,
            # Print
            PRN: self.handle_prn,
            # Multuiply
            MUL: self.handle_mul,
            # Halt
            HLT: self.handle_hlt,
            # Push to stack
            PUSH: self.handle_push,
            # Pop from stack
            POP: self.handle_pop
        }

    def load(self):
        # Initialize address counter
        address = 0
        # Open programs from the example folder
        program = []
        f = open(f'examples/{sys.argv[1]}', 'r')
        program = f.read().split('\n')
        program = [int(line.split('#')[0], 2) for line in program if line != '' and line[0] != '#']

        # For each instruction in the program
        for instruction in program:
            # Write the instruction to an address in RAM
            self.ram_write(instruction, address)
            # Increment address
            address += 1

    # Load register value
    def handle_ldi(self, reg, val):
        self.reg[reg] = val

    # Print helper function
    def handle_prn(self, reg, *args):
        print(self.reg[reg])

    # Multiplication helper function
    def handle_mul(self, reg_a, reg_b):
        self.reg[reg_a] *= self.reg[reg_b]

    # Halt program helper function
    def handle_hlt(self, *args):
        exit()

    # Push to stack
    def handle_push(self, reg, *args):
        # Increment stack pointer
        self.reg[SP] += 1
        self.ram_write(self.reg[reg], self.reg[SP])

    # Pop from stack
    def handle_pop(self, reg, *args):
        if self.reg[SP] == 0xF4:
            return None
        val = self.ram_read(self.reg[SP])
        # Decrement stack pointer
        self.reg[SP] -= 1
        self.reg[reg] = val 

    def ram_read(self, MAR):
        # Returns a memory address register in RAM
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        # Sets the the ram value at that memory address
        # register to the memory data register
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # If we're given an ADD operation
        if op == "ADD":
            # Increment the first value by the second
            self.reg[reg_a] += self.reg[reg_b]
        # If we're given a MUL operation (multiplication)
        elif op == "MUL":
            # Multiply those the first value by the second
            self.reg[reg_a] *= self.reg[reg_b]
        # Otherwise the operation is unsupported
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def run(self):
        """Run the CPU."""
        # Set program counter to zero
        self.pc = 0
        # Set halted to false
        halted = False
        # While the program isn't halted
        while not halted:
            # Instruction register reads program counter
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            op_count = IR >> 6
            self.branch_table[IR](operand_a, operand_b)
            self.pc += op_count + 1

# Program runs with
'''
python3 ls8.py /examplefile.ls8
'''
