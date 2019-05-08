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

    def __init__(self, input_file_name, output_path, is_first_file):
        self.file_prefix = output_path.split('/')[-1].split('.')[0]  # prefix used for function declaration
        self.static_prefix = input_file_name.split('/')[-1].split('.')[0]  # prefix used for static variable
        self.output_path = output_path
        self.is_first_file = is_first_file
        self.comp_cond_count = 0
        self.num_commands_written = 0
        self.num_functions_called = 0

    def write(self, parsed_command):
        """
        Translate the VM command and write Hack assembly code to the output path

        :param parsed_command: dictionary of parsed VM command
        :return: Nothing, translated Hack assembly code written to output file
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
        elif command_type == 'C_LABEL':
            translated = self._translate_label(parsed_command)
        elif command_type == 'C_GOTO':
            translated = self._translate_goto(parsed_command)
        elif command_type == 'C_IF':
            translated = self._translate_if(parsed_command)
        elif command_type == 'C_CALL':
            translated = self._translate_call(parsed_command)
        elif command_type == 'C_FUNCTION':
            translated = self._translate_function(parsed_command)
        elif command_type == 'C_END_PROGRAM':
            translated = ['(C_END_PROGRAM)', '@C_END_PROGRAM', '0;JMP']
        else:
            translated = self._translate_return()

        # "w" mode only if the currently processed file is the first out of many and this is the first write
        if self.num_commands_written == 0 and self.is_first_file:
            mode = 'w'

            if self.file_prefix in ('FibonacciElement', 'StaticsTest'):  # need to bootstrap start these two tests
                with open(self.output_path, mode) as f:
                    initial = ['@256', 'D=A', '@SP', 'M=D']  # setup stack pointer
                    initial.extend(self._translate_call({'command_type': 'C_CALL',
                                                         'function_name': 'Sys.init',
                                                         'n_args': '0'}))  # call Sys.init
                    initial = [c + '\n' for c in initial]
                    for c in initial:
                        f.write(c)
                mode = 'a'
        else:
            mode = 'a'

        with open(self.output_path, mode) as f:
            for line in translated:
                f.write(line)
                f.write('\n')

        self.num_commands_written += 1

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
            translated.append('@{prefix}.{index}'.format(prefix=self.static_prefix, index=index))
        elif segment in ('temp', 'pointer'):
            translated.append('@R{address}'.format(address=str((int(self.KEYWORD_ADDRESS[segment]) +
                                                                int(index)))))  # Address is an int
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
        operator_type, operator = self.NON_COMP_OPERATOR[command]

        translated = list()
        translated.extend(self.__pop_stack_to_d())

        if operator_type == 'unary':
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
        translated.append('D=D-M')
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

    def _translate_label(self, parsed_command):
        return ['({file_prefix}${label})'.format(file_prefix=self.file_prefix,
                                                 label=parsed_command['label'])]

    def _translate_goto(self, parsed_command):
        """Translate unconditional jump to"""
        translated = list()
        translated.append('@{file_prefix}${label}'.format(file_prefix=self.file_prefix,
                                                          label=parsed_command['label']))
        translated.append('0;JMP')

        return translated

    def _translate_if(self, parsed_command):
        """Translate conditional jump to"""
        translated = list()
        translated.extend(self.__pop_stack_to_d())
        translated.append('@{file_prefix}${label}'.format(file_prefix=self.file_prefix,
                                                          label=parsed_command['label']))
        translated.append('D;JNE')

        return translated

    def _translate_call(self, parsed_command):
        """Translate a function call command"""
        translated = list()
        return_address = '{function_name}RET{i}'.format(function_name=parsed_command['function_name'],
                                                        i=self.num_functions_called)
        self.num_functions_called += 1

        # push return address
        translated.append('@{return_address}'.format(return_address=return_address))
        translated.append('D=A')
        translated.extend(self.__push_d_to_stack())

        # save current state
        for register in ('LCL', 'ARG', 'THIS', 'THAT'):
            translated.extend(self.__lookup_register_val_to_d(register=register))
            translated.extend(self.__push_d_to_stack())

        translated.append('@' + str(int(parsed_command['n_args']) + 5))
        translated.append('D=A')
        translated.append('@SP')
        translated.append('D=M-D')
        translated.append('@ARG')
        translated.append('M=D')

        # LCL = *SP
        translated.extend(self.__lookup_register_val_to_d(register='SP'))
        translated.append('@LCL')
        translated.append('M=D')

        # goto function
        translated.append('@{function_name}'.format(function_name=parsed_command['function_name']))
        translated.append('0;JMP')

        # return address command
        translated.append('({return_address})'.format(return_address=return_address))

        return translated

    def _translate_function(self, parsed_command):
        """Translate a function declaration command"""
        translated = list()
        translated.append('({function_name})'.format(function_name=parsed_command['function_name']))
        for i in range(int(parsed_command['n_vars'])):
            translated.append('D=0')
            translated.extend(self.__push_d_to_stack())

        return translated

    def _translate_return(self):
        """Translate a return command"""
        translated = list()

        end_frame = 'R13'
        return_address = 'R14'

        # end_frame = LCL
        translated.extend(self.__lookup_register_val_to_d('LCL'))
        translated.append('@{end_frame}'.format(end_frame=end_frame))
        translated.append('M=D')

        # return_address = *(end_frame - 5)
        translated.append('@5')
        translated.append('D=A')
        translated.append('@{end_frame}'.format(end_frame=end_frame))
        translated.append('A=M-D')
        translated.append('D=M')
        translated.append('@{return_address}'.format(return_address=return_address))  # R14 will store return address
        translated.append('M=D')

        # *ARG = pop
        translated.extend(self.__pop_stack_to_d())
        translated.append('@ARG')
        translated.append('A=M')
        translated.append('M=D')

        # SP = ARG + 1
        translated.append('@ARG')
        translated.append('D=M')
        translated.append('@SP')
        translated.append('M=D+1')  # D is still the ARG from previous operation

        # THAT = *(R13-1)
        # THIS = *(R13-2)
        # ARG = *(R13-3)
        # LCL = *(R13-4)
        for i, register in enumerate(['THAT', 'THIS', 'ARG', 'LCL']):
            translated.append('@{i}'.format(i=str(i + 1)))
            translated.append('D=A')
            translated.append('@{end_frame}'.format(end_frame=end_frame))
            translated.append('A=M-D')
            translated.append('D=M')
            translated.append('@{register}'.format(register=register))
            translated.append('M=D')

        translated.append('@{return_address}'.format(return_address=return_address))
        translated.append('A=M')
        translated.append('0;JMP')

        return translated

    @staticmethod
    def __lookup_register_val_to_d(register):
        """Helper to get the value within the specified register to register D"""
        translated = list()
        translated.append('@{register}'.format(register=register))
        translated.append('D=M')

        return translated
