class CodeWriter:
    NON_COMP_OPERATOR = {
        'and': ('binary', '&'),
        'or': ('binary', '|'),
        'not': ('unary', '!'),
        'neg': ('unary', '-'),
        'add': ('binary', '+'),
        'sub': ('binary', 'sub')
    }

    COMP_OPERATOR = {
        'eq': 'JEQ',
        'gt': 'JGT',
        'lt': 'JLT'
    }

    def __init__(self, input_file_name, output_path):
        self.file_prefix = input_file_name.split('.')[0]
        self.output_path = output_path
        self.comp_cond_count = 0
        self.num_commands_written = 0

    def write(self, parsed_command):
        command_type = parsed_command['command_type']
        if command_type == 'C_ARITHMETIC' and parsed_command['command'] in self.COMP_OPERATOR:
            translated = self._translate_arithmetic_comp(parsed_command)
        elif command_type == 'C_ARITHMETIC' and parsed_command['command'] in self.NON_COMP_OPERATOR:
            translated = self._translate_arithmetic_nocomp(parsed_command)
        elif command_type == 'C_PUSH':
            translated = self._translate_push(parsed_command)
        elif command_type == 'C_POP':
            translated = self._translate_pop(parsed_command)

        mode = 'w' if self.num_commands_written == 0 else 'a'

        with open(self.output_path, mode) as f:
            for line in translated:
                f.write(line)
                f.write('\n')

    def _translate_push(self, parsed_command):
        translated = self.__resolve_address(parsed_command)
        translated.append('D=M')
        translated.extend(self.__push_d_to_stack())

        return translated

    def __resolve_address(self, parsed_command):
        """
        This helper function assigns the right address to the A register depending on the
        segment given in the parsed command

        :param parsed_command:
        :return:
        """
        segment = parsed_command['segment']
        index = parsed_command['index']
        translated = []
        if segment in ('local', 'argument', 'this', 'that'):
            translated.append('@{index}'.format(index=index))
            translated.append('D=A')
            translated.append('@{segment}'.format(segment=segment.upper()))
            translated.append('A=M+D')
        elif segment == 'constant':
            translated.append('@{index}'.format(index=index))
        elif segment == 'static':
            translated.append('@{prefix}.{index}'.format(prefix=self.file_prefix, index=index))
        elif segment == 'temp':
            translated.append('@{index}'.format(index=index))
            translated.append('D=M')
            translated.append('@5')  # temp segment base address starts at 5
            translated.append('A=A+D')
        else:
            converted_parsed_command = self.__convert_pointer(parsed_command)
            return self.__resolve_address(converted_parsed_command)

        return translated

    @staticmethod
    def __convert_pointer(parsed_command):
        """Depending on whether the index is 0 or 1 convert the segment to 'this' or 'that'"""
        new_parsed_command = parsed_command.copy()
        if parsed_command['index'] == '0':
            new_parsed_command['segment'] = 'this'
        elif parsed_command['index'] == '1':
            new_parsed_command['segment'] = 'that'
        else:
            print(parsed_command['index'])
            raise ValueError('invalid index for segment pointer')

        return new_parsed_command

    @staticmethod
    def __push_d_to_stack():
        """Hack Assembly code to push the D register value onto the next available stack memory location"""
        translated = list()
        translated.append('@SP')
        translated.append('M=M+1')
        translated.append('A=M-1')
        translated.append('M=D')

        return translated

    @staticmethod
    def __pop_stack_to_d():
        """
        Hack Assembly code to pop the top of stack value to the D register
        """
        translated = list()
        translated.append('@SP')
        translated.append('M=M-1')
        translated.append('A=M')
        translated.append('D=M')

        return translated

    def _translate_pop(self, parsed_command):
        translated = self.__resolve_address(parsed_command)
        translated.append('D=A')
        translated.append('@R13')
        translated.append('M=D')
        translated.extend(self.__pop_stack_to_d())
        translated.append('@R13')
        translated.append('A=M')
        translated.append('M=D')

        return translated

    def _translate_arithmetic_nocomp(self, parsed_command):
        command = parsed_command['command']
        command_type, operator = self.NON_COMP_OPERATOR[command]

        translated = list()
        translated.extend(self.__pop_stack_to_d())

        if command_type == 'unary':
            translated.append('D={syntax}D'.format(syntax=operator))
            translated.extend(self.__push_d_to_stack())
            return translated

        translated.append('@R13')
        translated.append('M=D')
        translated.extend((self.__pop_stack_to_d()))
        translated.append('@R13')
        translated.append('D=M{syntax}D'.format(syntax=operator))
        translated.extend(self.__push_d_to_stack())

        return translated

    def _translate_arithmetic_comp(self, parsed_command):
        command = parsed_command['command']
        directive = self.COMP_OPERATOR[command]
        translated = list()
        translated.extend(self.__pop_stack_to_d())
        translated.append('@R13')
        translated.append('M=D')
        translated.extend((self.__pop_stack_to_d()))
        translated.append('@R13')
        translated.append('D=M-D')
        translated.append('@COND_TRUE_{i}'.format(i=self.comp_cond_count))
        translated.append('D;{directive}'.format(directive=directive))
        translated.append('D=0')  # does not satisfy the condition
        translated.extend(self.__push_d_to_stack())
        translated.append('@END_COND_{i}'.format(i=self.comp_cond_count))
        translated.append('0;JMP')  # unconditional jump to exit comparison control flow
        translated.append('(COND_TRUE_{i})'.format(i=self.comp_cond_count))
        translated.append('D=-1')  # -1 = true
        translated.extend(self.__push_d_to_stack())
        translated.append('(END_COND_{i})'.format(i=self.comp_cond_count))
        self.comp_cond_count += 1

        return translated
