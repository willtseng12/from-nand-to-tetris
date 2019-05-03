class HackAssembler:

    INSTRUCTIONS = {
        '0'    : '0101010',
        '1'    : '0111111',
        '-1'   : '0111010',
        'D'    : '0001100',
        'A'    : '0110000',
        '!D'   : '0001101',
        '!A'   : '0110001',
        '-D'   : '0001111',
        '-A'   : '0110011',
        'D+1'  : '0011111',
        'A+1'  : '0110111',
        'D-1'  : '0001110',
        'A-1'  : '0110010',
        'D+A'  : '0000010',
        'D-A'  : '0010011',
        'A-D'  : '0000111',
        'D&A'  : '0000000',
        'D|A'  : '0010101',
        'M'    : '1110000',
        '!M'   : '1110001',
        '-M'   : '1110011',
        'M+1'  : '1110111',
        'M-1'  : '1110010',
        'D+M'  : '1000010',
        'D-M'  : '1010011',
        'M-D'  : '1000111',
        'D&M'  : '1000000',
        'D|M'  : '1010101',
    }

    DESTINATION = {
        '0'   : '000',
        'M'   : '001',
        'D'   : '010',
        'MD'  : '011',
        'A'   : '100',
        'AM'  : '101',
        'AD'  : '110',
        'ADM' : '111'
    }

    JUMP = {
        '0'   : '000',
        'JGT' : '001',
        'JEQ' : '010',
        'JGE' : '011',
        'JLT' : '100',
        'JNE' : '101',
        'JLE' : '110',
        'JMP' : '111'
    }

    def __init__(self, path):
        self.st = {'R0': 0,
                   'R1': 1,
                   'R2': 2,
                   'R3': 3,
                   'R4': 4,
                   'R5': 5,
                   'R6': 6,
                   'R7': 7,
                   'R8': 8,
                   'R9': 9,
                   'R10': 10,
                   'R11': 11,
                   'R12': 12,
                   'R13': 13,
                   'R14': 14,
                   'R15': 15,
                   'SCREEN': 16384,
                   'KBD': 24576,
                   'SP': 0,
                   'LCL': 1,
                   'ARG': 2,
                   'THIS': 3,
                   'THAT': 4}
        self.instructions = self._get_instruction(path)
        self.next_avail_reg = 16

    def assemble(self, path_to_file):
        self._build_st()
        bin_list = self._parse_instruction()
        with open(path_to_file, 'w') as f:
            for bins in bin_list:
                f.write(bins)
                f.write('\n')

    def _parse_instruction(self):
        parsed = []
        for instr in self.instructions:
            if instr.startswith('(') and instr.endswith(')'): # skip pseudo symbols
                continue
            if instr.startswith('@'):
                binaries = self.__parse_a_instruction(instr)
            else:
                binaries = self.__parse_c_instruction(instr)
            parsed.append(binaries)
        return parsed

    def __parse_a_instruction(self, instruction):
        symbol = instruction[1:]
        try:
            val = int(symbol)
        except ValueError:
            val = self.st.get(symbol)
        if val is not None:
            binary = '0{}'.format('{0:015b}'.format(val))
        else:
            self.st[symbol] = self.next_avail_reg
            binary = '0{}'.format('{0:015b}'.format(self.next_avail_reg))
            self.next_avail_reg += 1
        return binary

    def __parse_c_instruction(self, instruction):
        bin_list = ['111', '0000000', '000', '000']  # prefix for C instruction
        if '=' in instruction:  # non null d
            dest_split = instruction.split('=')
            dest = dest_split[0].strip()
            bin_list[2] = self.DESTINATION[dest]
            comp_and_jmp = dest_split[1].strip()
            if ';' in comp_and_jmp:
                comp_split = comp_and_jmp.split(';')
                comp, jmp = comp_split[0].strip(), comp_split[1].strip()
                bin_list[1] = self.INSTRUCTIONS[comp]
                bin_list[3] = self.JUMP[jmp]
            else:
                bin_list[1] = self.INSTRUCTIONS[comp_and_jmp]
        elif ';' in instruction:
            comp_split = instruction.split(';')
            comp, jmp = comp_split[0].strip(), comp_split[1].strip()
            bin_list[1] = self.INSTRUCTIONS[comp]
            bin_list[3] = self.JUMP[jmp]

        return ''.join(bin_list)

    def _build_st(self):
        i = 0
        for instr in self.instructions:
            if instr.startswith('(') and instr.endswith(')'):
                self.st[instr.lstrip('(').rstrip(')')] = i
                continue
            i += 1

    @staticmethod
    def _get_instruction(path):
        instructions = []
        with open(path, 'r') as f:
            file = f.read().split("\n")
            for line in file:
                l = line.strip()
                if l.startswith('//') or l == '':
                    continue
                else:
                    instructions.append(l.split('//')[0].strip())
        return instructions


if __name__ == '__main__':
    add_assembler = HackAssembler('add/Add.asm')
    add_assembler.assemble('add/Add.hack')

    max_assembler = HackAssembler('max/Max.asm')
    max_assembler.assemble('max/Max.hack')

    rect_assembler = HackAssembler('rect/Rect.asm')
    rect_assembler.assemble('rect/Rect.hack')

    pong_assembler = HackAssembler('pong/Pong.asm')
    pong_assembler.assemble('pong/Pong.hack')
