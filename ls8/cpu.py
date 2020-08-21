import sys

LDI  = 0b10000010
PRN  = 0b01000111
HLT  = 0b00000001
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
'''
the JMP instruction performs an unconditional jump.
Such an instruction transfers the flow of execution by
changing the instruction pointer register.
'''
JMP  = 0b01010100
# Jump if equal
JEQ  = 0b01010101
'''
The jnz (or jne) instruction is a conditional jump that follows a test.
It jumps to the specified location if the Zero Flag (ZF) is cleared (0).
jnz is commonly used to explicitly test for something not being equal to
zero whereas jne is commonly found after a cmp instruction.
'''
JNE  = 0b01010110

SP   = 7
ADD  = 0b0000
AND  = 0b1000
'''
The CMP instruction subtracts the value of Operand2 from the value in Rn.
This is the same as a SUBS instruction, except that the result is discarded.
'''
CMP  = 0b0111
DEC  = 0b0110
DIV  = 0b0011
INC  = 0b0101
MOD  = 0b0100
MUL  = 0b0010
NOT  = 0b1001
OR   = 0b1010
SHL  = 0b1100
SHR  = 0b1101
SUB  = 0b0001
XOR  = 0b1011

class CPU:

    def __init__(self):
        # RAM: Working data
        self.ram = [0] * 256
        # Register: used to store data/instruction in-execution
        self.reg = [0] * 8
        # Register stack pointer
        self.reg[SP] = 0xF4
        # Program counter
        self.pc = 0
        self.fl = 0
        self.branch_table = {
            LDI:  self.handle_ldi,
            PRN:  self.handle_prn,
            HLT:  self.handle_hlt,
            PUSH: self.handle_push,
            POP:  self.handle_pop,
            CALL: self.handle_call,
            RET:  self.handle_ret,
            JMP:  self.handle_jump,
            JEQ:  self.handle_jump,
            JNE:  self.handle_jump
        }

    def load(self):
        address = 0
        program = []
        f = open(f'examples/{sys.argv[1]}', 'r')
        program = f.read().split('\n')
        program = [int(line.split('#')[0], 2) for line in program if line != '' and line[0] != '#']

        for instruction in program:
            self.ram_write(instruction, address)
            address += 1

    # LDR stores the source register's value plus an 
    # immediate value offset and stores it in the destination register
    def handle_ldi(self, reg, val, *args):
        self.reg[reg] = val

    # PRN prints the current value in our destination register
    def handle_prn(self, reg, *args):
        print(self.reg[reg])

    # Stop program
    def handle_hlt(self, *args):
        exit()

    def ram_read(self, MAR):
        # Returns current memory address register value in RAM
        return self.ram[MAR]
        
    # Feeds the MAR into the memory data register to be used by CPU
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    # An arithmetic logic unit (ALU) is a digital circuit
    # used to perform arithmetic and logic operations
    def alu(self, op, reg_a, reg_b):
        val_a = self.reg[reg_a]
        val_b = self.reg[reg_b] if reg_b < 8 else 0
        # Define operations ALSO STRETCH GOALS
        switch = {
            ADD: val_a + val_b,
            AND: val_a & val_b,
            DEC: val_a - 1,
            DIV: val_a / val_b if val_b != 0 else None,
            INC: val_a + 1,
            MOD: val_a % val_b if val_b != 0 else None,
            MUL: val_a * val_b,
            NOT: ~val_a & 0xff,
            OR:  val_a | val_b,
            SHL: val_a << val_b,
            SHR: val_a >> val_b,
            SUB: val_a - val_b,
            XOR: val_a ^ val_b
        }
        # If the operation is in the dict above
        if op in switch:
            # Set the value to that op
            val = switch[op]
            # Edge case: divide by 0
            if val is None:
                print('Error: Attempted to divide by 0')
                self.handle_hlt()
            # If valid 
            else:
                # Set that value to op1 in register
                self.reg[reg_a] = val
        # If we're dealing with a CMP op
        elif op == CMP:
            # If op1 is smaller than op2
            if val_a < val_b:
                # Set flag to 4 - False
                self.fl = 0b100
            elif val_a > val_b:
                # Set flag to 2 - False
                self.fl = 0b010
            else:
                # Set flag to 1 - True
                self.fl = 0b001
        # If not in switch or CMP
        else:
            raise Exception("Unsupported ALU operation")
            

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def run(self):
        self.pc = 0
        halted = False

        while not halted:
            IR         = self.ram_read(self.pc)
            op_count   = IR >> 6
            is_alu_op  = (IR & 0b100000) >> 5
            mutates_pc = (IR & 0b10000) >> 4
            operand_a  = self.ram_read(self.pc+1)
            operand_b  = self.ram_read(self.pc+2)

            if is_alu_op:
                op = IR & 0b00001111
                self.alu(op, operand_a, operand_b)
            else:
                self.branch_table[IR](operand_a, operand_b, IR)

            if not mutates_pc:
                self.pc += op_count+1

    def handle_push(self, reg, call=None, *args):
        self.reg[SP] += 1
        if call == True:
            self.ram_write(reg, self.reg[SP])
        else:
            self.ram_write(self.reg[reg], self.reg[SP])

    def handle_pop(self, reg=None, *args):
        if self.reg[SP] == 0xF4:
            return None
        val = self.ram_read(self.reg[SP])
        self.reg[SP] -= 1
        if reg is not None:
            self.reg[reg] = val
        else:
            return val

    def handle_call(self, reg, *args):
        self.handle_push(self.pc+2, call=True)
        self.pc = self.reg[reg]
    
    def handle_ret(self, *args):
        self.pc = self.handle_pop()

    def handle_jump(self, reg, _, IR):
        # Add equal flag || 0 || True
        equal = self.fl & 0b00000001
        if IR == JEQ and equal:
            pass
        elif IR == JNE and not equal:
            pass
        elif IR == JMP:
            pass
        else:
            self.pc += 2
            return
        self.pc = self.reg[reg]