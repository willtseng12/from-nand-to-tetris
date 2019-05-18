class VMWriter:
    def __init__(self, out_file_name):
        self.out_file_name = out_file_name
        self.writer = open(out_file_name, 'w')

    def write_push(self, segment, index):
        self.writer.write(f'push {segment} {index}\n')
        self.writer.flush()

    def write_pop(self, segment, index):
        self.writer.write(f'pop {segment} {index}\n')
        self.writer.flush()

    def write_arithmetic(self, operator, is_unary=None):
        if operator == '-':
            assert is_unary is not None

        if operator == '+':
            self.writer.write('add\n')
        elif operator == '-' and is_unary == False:
            self.writer.write('sub\n')
        elif operator == '-' and is_unary == True:
            self.writer.write('neg\n')
        elif operator == '~':
            self.writer.write('not\n')
        elif operator == '<':
            self.writer.write('lt\n')
        elif operator == '>':
            self.writer.write('gt\n')
        elif operator == '&':
            self.writer.write('and\n')
        elif operator == '|':
            self.writer.write('or\n')
        elif operator == '=':
            self.writer.write('eq\n')
        elif operator == '/':
            self.writer.write('call Math.divide 2\n')
        elif operator == '*':
            self.writer.write('call Math.multiply 2\n')
        else:
            raise ValueError(f'{operator} is not an operator')

        self.writer.flush()

    def write_label(self, label):
        self.writer.write(f'label {label}\n')
        self.writer.flush()

    def write_goto(self, label):
        self.writer.write(f'goto {label}\n')
        self.writer.flush()

    def write_if_goto(self, label):
        self.writer.write(f'if-goto {label}\n')
        self.writer.flush()

    def write_call(self, name, n_args):
        self.writer.write(f'call {self.out_file_name}.{name} {n_args}\n')
        self.writer.flush()

    def write_function(self, name, n_locals):
        self.writer.write(f'call {self.out_file_name}.{name} {n_args}\n')
        self.writer.flush()

    def write_return(self):
        self.writer.write('return\n')

    def writer_close(self):
        self.writer.close()
