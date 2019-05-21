class VMWriter:
    def __init__(self, out_file_name):
        self.out_file_name = out_file_name
        self.out_file_prefix = out_file_name.split('.')[0]
        self.writer = open(out_file_name, 'w')

    def write_push(self, segment, index):
        self.writer.write('push {segment} {index}\n'.format(segment=segment,
                                                            index=index))

    def write_pop(self, segment, index):
        self.writer.write('pop {segment} {index}\n'.format(segment=segment,
                                                           index=index))

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
            raise ValueError('{operator} is not an operator'.format(operator=operator))

    def write_label(self, label):
        self.writer.write('label {label}\n'.format(label=label))

    def write_goto(self, label):
        self.writer.write('goto {label}\n'.format(label=label))

    def write_if_goto(self, label):
        self.writer.write('if-goto {label}\n'.format(label=label))

    def write_call(self, name, n_args):
        self.writer.write('call {name} {n_args}\n'.format(name=name, n_args=n_args))

    def write_subroutine(self, name, n_locals):
        self.writer.write('function {class_name}.{name} {n_locals}\n'
                          .format(class_name=self.out_file_prefix,
                                  name=name,
                                  n_locals=n_locals))

    def write_return(self):
        self.writer.write('return\n')

    def writer_close(self):
        self.writer.close()
