"""CPU functionality."""

import sys

LDI = 0b10000010

PRN = 0b01000111

HLT = 0b00000001

MUL = 0b10100010

ADD = 0b10100000

PUSH = 0b01000101

POP = 0b01000110

CALL = 0b01010000

RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 255
        self.pc = 0
        self.SP = 7
        self.reg[self.SP] = 0xF4
        self.FL = [0] * 8

        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[ADD] = self.handle_add
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret

    def load(self):
        """Load a program into memory."""

        address = 0
        filename = sys.argv[1]
        with open(filename) as f:
            for line in f:
                comment_split = line.split("#")
                num = comment_split[0].strip()

                if num == "":
                    continue

                val = int(num, 2)
                self.ram[address] = val
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def handle_prn(self, *argv):
        print(self.reg[argv[0]])
        self.pc += 2

    def handle_ldi(self, *argv):
        self.reg[argv[0]] = argv[1]
        self.pc += 3

    def handle_hlt(self, *argv):
        self.pc += 1
        sys.exit()

    def handle_mul(self, *argv):
        self.alu("MUL", argv[0], argv[1])
        self.pc += 3

    def handle_add(self, *argv):
        self.alu("ADD", argv[0], argv[1])
        self.pc += 3

    def handle_push(self, *argv):
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.reg[argv[0]]
        self.pc += 2

    def handle_pop(self, *argv):
        val = self.ram[self.reg[self.SP]]
        self.reg[argv[0]] = val
        self.reg[self.SP] += 1
        self.pc += 2

    def handle_call(self, *argv):
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + 2
        reg = argv[0]
        self.pc = self.reg[reg]

    def handle_ret(self, *argv):
        self.pc = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

    def run(self):
        """Run the CPU."""

        running = True

        while running:

            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if instruction in self.branchtable:
                self.branchtable[instruction](operand_a, operand_b)
            else:
                print("did not understand the instruction")
                running = False
