class CodeWriter:
    NON_COMP_OPERATOR = {
        'and': ('binary', '&'),
        'or': ('binary', '|'),
        'not': ('unary', '!'),
        'neg': ('unary', '-'),
        'add': ('binary', '+'),
        'sub': ('binary', '-')
    }

    COMP_OPERATOR = {
        'eq': 'JEQ',
        'gt': 'JGT',
        'lt': 'JLT'
    }
	
	KEYWORD_ADDRESS = {
        'local': 'LCL',
        'argument': 'ARG',
        'this': 'THIS',
        'that': 'THAT',
        'temp': '5',
		'pointer': '3'}

    def __init__(self, input_file_name, output_path):
        self.file_prefix = input_file_name.split('.')[0]
        self.output_path = output_path
        self.comp_cond_count = 0
        self.num_commands_written = 0

    def write(self, parsed_command):
        """
        Translate the VM command and write Hack assembly code to the output path

        :param parsed_command: dictionary of parsed VM command
        :return: Nothing, translated Hack assembly code written to output path
        """
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
        """Translates a push command"""
        translated = self.__resolve_address(parsed_command)
        if parsed_command['segment'] == 'constant':
            translated.append('D=A')
        else:
            translated.append('D=M')
        translated.extend(self.__push_d_to_stack())

        return translated

    def __resolve_address(self, parsed_command):
        """
        This helper function assigns the right address to the A register depending on the
        segment given in the parsed command

        :param parsed_command: dictionary of parsed VM command
        :return: List, list of translated commands up until the assignment of the right address to register A
        """
        segment = parsed_command['segment']
        index = parsed_command['index']
        translated = []
        if segment in ('local', 'argument', 'this', 'that'):
            translated.append('@{index}'.format(index=index))
            translated.append('D=A')
            translated.append('@{address}'.format(address=self.KEYWORD_ADDRESS[segment]))
            translated.append('A=M+D')
        elif segment == 'constant':
            translated.append('@{index}'.format(index=index))
        elif segment == 'static':
            translated.append('@{prefix}.{index}'.format(prefix=self.file_prefix, index=index))
        elif segment in ('temp', 'pointer'):
            translated.append('@R{address}'.format(address=str((int(self.KEYWORD_ADDRESS[segment]) +
                                                                int(index))))) # Address is an int
        else:
            raise ValueError('segment not recognized: {segment}'.format(segment=segment))

        return translated

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
        """ Hack Assembly code to pop the top of stack value to the D register"""
        translated = list()
        translated.append('@SP')
        translated.append('M=M-1')
        translated.append('A=M')
        translated.append('D=M')

        return translated

    def _translate_pop(self, parsed_command):
        """Translates a pop command"""
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
        """Translates a arithmetic command that has is no a comparison statement"""
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
        translated.append('D=D{syntax}M'.format(syntax=operator))
        translated.extend(self.__push_d_to_stack())

        return translated

    def _translate_arithmetic_comp(self, parsed_command):
        """Translates a arithmetic command that has is a comparison statement"""
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
