import os
import sys

from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from vm_writer import VMWriter


class CompilationEngine:

    def __init__(self, tokenizer, out_file_name, symbol_table, vm_writer):
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
        self.out_file_name = out_file_name
        self.out_file_prefix = out_file_name.split('.')[0]
        self.if_label_index = 0
        self.while_label_index = 0

    def compile(self):
        self.compile_class()

    def compile_class(self):
        self.tokenizer.advance()  # first token
        self.check_required_token(self.tokenizer.key_word(), 'class')
        self.tokenizer.advance()  # class name

        self.tokenizer.advance()  # {

        self.check_required_token(self.tokenizer.key_word(), '{')
        self.tokenizer.advance()

        while self.tokenizer.symbol() in ('field', 'static'):
            self.compile_class_var_dec()

        while self.tokenizer.key_word() in ('constructor', 'function', 'method'):
            self.compile_subroutine_dec()

        self.check_required_token(self.tokenizer.key_word(), '}')

    def compile_class_var_dec(self):
        variable_kind = self.tokenizer.key_word()
        self.tokenizer.advance()

        variable_type = self.tokenizer.key_word()
        self.tokenizer.advance()

        variable_name = self.tokenizer.identifier()
        self.tokenizer.advance()

        self.symbol_table.define(name=variable_name, type=variable_type, kind=variable_kind)

        while self.tokenizer.symbol() == ',':
            # skip comma
            self.tokenizer.advance()

            variable_name = self.tokenizer.identifier()
            self.tokenizer.advance()

            self.symbol_table.define(name=variable_name, type=variable_type, kind=variable_kind)

        # skip ;
        self.tokenizer.advance()

    def compile_subroutine_dec(self):

        self.symbol_table.start_sub_routine()

        if self.tokenizer.key_word() == 'method':
            self.tokenizer.advance()  # class type
            return_type = self.tokenizer.identifier()
            self.symbol_table.define(name='this', type=return_type, kind='argument')
            is_void = return_type == 'void'
            self.tokenizer.advance()  # method name
            subroutine_name = self.tokenizer.identifier()
            self.tokenizer.advance()  # (
            self.compile_parameter_list()
            self.tokenizer.advance()  # {
            self.compile_subroutine_body(name=subroutine_name, type='method', is_void=is_void)

        elif self.tokenizer.key_word() == 'constructor':
            self.tokenizer.advance()  # return type
            is_void = self.tokenizer.identifier() == 'void'
            self.tokenizer.advance()  # new
            subroutine_name = self.tokenizer.identifier()
            self.tokenizer.advance()  # (
            self.compile_parameter_list()
            self.tokenizer.advance()  # {
            self.compile_subroutine_body(name=subroutine_name, type='constructor', is_void=is_void)

        elif self.tokenizer.key_word() == 'function':
            self.tokenizer.advance()  # return type
            is_void = self.tokenizer.identifier() == 'void'
            self.tokenizer.advance()  # function name
            subroutine_name = self.tokenizer.identifier()
            self.tokenizer.advance()  # (

            self.compile_parameter_list()
            self.tokenizer.advance()  # {
            self.compile_subroutine_body(name=subroutine_name, type='function', is_void=is_void)

    def compile_parameter_list(self):

        self.check_required_token(self.tokenizer.symbol(), '(')
        self.tokenizer.advance()  # param_type

        while self.tokenizer.symbol() != ')':
            param_type = self.tokenizer.identifier()
            self.tokenizer.advance()  # param name

            param_name = self.tokenizer.identifier()
            self.tokenizer.advance()  # , or )
            self.symbol_table.define(name=param_name, type=param_type, kind='argument')

            if self.tokenizer.symbol() == ',':
                self.tokenizer.advance()

    def compile_subroutine_body(self, name, type, is_void):

        self.check_required_token(self.tokenizer.symbol(), '{')
        self.tokenizer.advance()  # subroutine body

        while self.tokenizer.symbol() == 'var':
            self.tokenizer.advance()  # skip 'var'
            self.compile_var_dec()

        local_var_count = self.symbol_table.var_count(kind='var')
        if type == 'method':
            self.vm_writer.write_subroutine(name='{subroutine_name}'
                                            .format(subroutine_name=name),
                                            n_locals=local_var_count + 1)
            self.vm_writer.write_push(segment='argument', index=0)
            self.vm_writer.write_pop(segment='pointer', index=0)
        elif type == 'constructor':
            self.vm_writer.write_subroutine(name='{subroutine_name}'
                                            .format(subroutine_name=name),
                                            n_locals=0)
            num_instance_variable = self.symbol_table.var_count(kind='field')
            self.vm_writer.write_push(segment='constant', index=num_instance_variable)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop(segment='pointer', index=0)
        elif type == 'function':
            self.vm_writer.write_subroutine(name='{subroutine_name}'
                                            .format(subroutine_name=name),
                                            n_locals=local_var_count)

        self.compile_statements(is_void=is_void)

        # }
        self.check_required_token(self.tokenizer.symbol(), '}')
        self.tokenizer.advance()

    def compile_var_dec(self):

        # local variable type
        variable_type = self.tokenizer.identifier()
        self.tokenizer.advance()

        # local variable name
        variable_name = self.tokenizer.identifier()
        self.tokenizer.advance()

        self.symbol_table.define(name=variable_name, type=variable_type, kind='var')

        # potentially additional variable name
        while self.tokenizer.symbol() == ',':
            self.tokenizer.advance()  # skip comma

            # local variable name
            variable_name = self.tokenizer.identifier()
            self.tokenizer.advance()

            self.symbol_table.define(name=variable_name, type=variable_type, kind='var')

        # ;
        self.check_required_token(self.tokenizer.symbol(), ';')
        self.tokenizer.advance()

    def compile_statements(self, is_void):
        while self.tokenizer.key_word() in ('let', 'if', 'while', 'do', 'return'):
            if self.tokenizer.key_word() == 'let':
                self.compile_let()

            elif self.tokenizer.key_word() == 'do':
                self.compile_do()

            elif self.tokenizer.key_word() == 'return':
                self.compile_return(is_void=is_void)

            elif self.tokenizer.key_word() == 'if':
                self.compile_if(is_void=is_void)

            elif self.tokenizer.key_word() == 'while':
                self.compile_while(is_void=is_void)

    def compile_do(self):
        # skip do
        self.tokenizer.advance()

        current_token, current_token_type = self.tokenizer.identifier(), self.tokenizer.token_type()
        self.tokenizer.advance()

        self._compile_subroutine_call(previous_token=current_token,
                                      previous_token_type=current_token_type)

        # ;
        self.check_required_token(self.tokenizer.symbol(), ';')
        self.tokenizer.advance()

        self.vm_writer.write_pop(segment='temp', index=0)  # pop void return 0

    def compile_let(self):

        # skip 'let'
        self.tokenizer.advance()
        # LHS

        # identifier
        assignee = self.tokenizer.identifier()
        assignee_segment = self.convert_kind_to_vm_keyword(self.symbol_table.kind_of(assignee))
        assignee_index = self.symbol_table.index_of(assignee)
        is_array = False

        self.tokenizer.advance()

        if self.tokenizer.symbol() == '[':  # array case
            self.tokenizer.advance()
            is_array = True
            # align the array pointer
            # self.vm_writer.write_push(segment=assignee_segment, index=assignee_index)

            self.compile_expression()
            self.vm_writer.write_push(segment=assignee_segment, index=assignee_index)

            self.check_required_token(self.tokenizer.key_word(), ']')
            self.tokenizer.advance()

            self.vm_writer.write_arithmetic(operator='+')

        self.check_required_token(self.tokenizer.key_word(), '=')
        self.tokenizer.advance()

        # RHS
        self.compile_expression()

        if is_array:
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            self.vm_writer.write_pop(assignee_segment, assignee_index)

        # ;
        self.check_required_token(self.tokenizer.key_word(), ';')
        self.tokenizer.advance()

    def compile_while(self, is_void):
        self.tokenizer.advance()  # skip while

        # (
        self.check_required_token(self.tokenizer.key_word(), '(')
        self.tokenizer.advance()

        label1 = 'while_{}'.format(self.while_label_index)
        self.while_label_index += 1
        label2 = 'while_{}'.format(self.while_label_index)
        self.while_label_index += 1

        self.vm_writer.write_label(label=label1)

        self.compile_expression()

        self.vm_writer.write_arithmetic(operator='~', is_unary=True)

        # )
        self.check_required_token(self.tokenizer.key_word(), ')')
        self.tokenizer.advance()

        self.vm_writer.write_if_goto(label=label2)

        # {
        self.check_required_token(self.tokenizer.key_word(), '{')
        self.tokenizer.advance()

        self.compile_statements(is_void=is_void)

        # }
        self.check_required_token(self.tokenizer.key_word(), '}')

        self.vm_writer.write_goto(label=label1)
        self.vm_writer.write_label(label=label2)
        self.tokenizer.advance()

    def compile_return(self, is_void):

        # skip return
        self.tokenizer.advance()

        if self.tokenizer.symbol() != ';':
            self.compile_expression()

        if is_void:
            self.vm_writer.write_push(segment='constant', index=0)
        # ;
        self.check_required_token(self.tokenizer.key_word(), ';')
        self.tokenizer.advance()
        self.vm_writer.write_return()

    def compile_if(self, is_void):
        self.tokenizer.advance()

        self.check_required_token(self.tokenizer.key_word(), '(')
        self.tokenizer.advance()

        self.compile_expression()
        self.vm_writer.write_arithmetic(operator='~', is_unary=True)

        label1 = 'if_{}'.format(self.if_label_index)
        self.if_label_index += 1

        self.vm_writer.write_if_goto(label=label1)

        self.check_required_token(self.tokenizer.key_word(), ')')
        self.tokenizer.advance()

        # {
        self.check_required_token(self.tokenizer.key_word(), '{')
        self.tokenizer.advance()

        self.compile_statements(is_void=is_void)

        self.check_required_token(self.tokenizer.key_word(), '}')
        self.tokenizer.advance()

        label2 = 'if_{}'.format(self.if_label_index)
        self.if_label_index += 1

        self.vm_writer.write_goto(label=label2)

        self.vm_writer.write_label(label=label1)

        # else?
        if self.tokenizer.key_word() == 'else':
            self.tokenizer.advance()

            self.check_required_token(self.tokenizer.key_word(), '{')
            self.tokenizer.advance()

            self.compile_statements(is_void=is_void)

            self.check_required_token(self.tokenizer.key_word(), '}')
            self.tokenizer.advance()

        self.vm_writer.write_label(label=label2)

    def compile_expression(self):
        self.compile_term()
        # (operator term)*
        while self.tokenizer.symbol() in self.tokenizer.jack_operator():
            converted_symbol = self.tokenizer.symbol()
            self.tokenizer.advance()

            self.compile_term()

            self.vm_writer.write_arithmetic(operator=converted_symbol, is_unary=False)

    def compile_term(self):

        # "(" expression ")" case
        if self.tokenizer.symbol() == '(':
            self.tokenizer.advance()

            self.compile_expression()

            self.check_required_token(self.tokenizer.key_word(), ')')
            self.tokenizer.advance()

        # unary op term case
        elif self.tokenizer.symbol() in ('-', '~'):
            unary_op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(operator=unary_op, is_unary=True)

        # empty expression list
        elif self.tokenizer.symbol() == ')':
            return

        # a constant, subroutine call, or array access
        # need to look ahead 1
        else:
            current_token, current_token_type = self.tokenizer.identifier(), self.tokenizer.token_type()
            self.tokenizer.advance()

            # subroutine call
            if self.tokenizer.symbol() in ('(', '.'):
                self._compile_subroutine_call(previous_token=current_token,
                                              previous_token_type=current_token_type)

            # array access
            elif self.tokenizer.symbol() == '[':

                segment = self.convert_kind_to_vm_keyword(self.symbol_table.kind_of(current_token))
                index = self.symbol_table.index_of(current_token)
                self.vm_writer.write_push(segment, index)

                self.tokenizer.advance()  # skip [

                self.compile_expression()

                # ]
                self.check_required_token(self.tokenizer.key_word(), ']')
                self.tokenizer.advance()

                self.vm_writer.write_arithmetic('+')
                self.vm_writer.write_pop('pointer', '1')
                self.vm_writer.write_push('that', '0')  # push the value of the accessed value on stack

            # Integer constant
            elif JackTokenizer.is_int_value(current_token):
                self.vm_writer.write_push('constant', current_token)

            # string constant
            elif current_token_type == 'stringConstant':

                num_character = len(current_token)
                self.vm_writer.write_push('constant', num_character)

                # call string constructor
                self.vm_writer.write_call('String.new', 1)

                for i in range(num_character):
                    self.vm_writer.write_push('constant', ord(current_token[i]))
                    self.vm_writer.write_call('String.appendChar', 2)

                # no need to advance again after string constant call

            # keyword constant
            elif current_token == 'true':
                self.vm_writer.write_push(segment='constant', index=1)
                self.vm_writer.write_arithmetic('-', is_unary=True)
            elif current_token in ('false', 'null'):
                self.vm_writer.write_push(segment='constant', index=0)
            elif current_token == 'this':
                self.vm_writer.write_push(segment='pointer', index=0)

            # var name
            else:
                segment = self.convert_kind_to_vm_keyword(self.symbol_table.kind_of(current_token))
                index = self.symbol_table.index_of(current_token)
                self.vm_writer.write_push(segment, index)

    def compile_expression_list(self):

        i = 0
        if self.tokenizer.symbol() != ')':
            self.compile_expression()
            i += 1

        while self.tokenizer.symbol() == ',':
            self.tokenizer.advance()
            self.compile_expression()
            i += 1

        return i

    def _compile_subroutine_call(self, previous_token, previous_token_type):

        # method
        if self.tokenizer.symbol() == '(':
            self.vm_writer.write_push(segment='pointer', index=0)
            self.tokenizer.advance()  # skip (

            n_args = self.compile_expression_list()

            self.check_required_token(self.tokenizer.symbol(), ')')
            self.tokenizer.advance()

            self.vm_writer.write_call(name=self.out_file_prefix + '.' + previous_token, n_args=n_args)

        # static method
        elif self.tokenizer.symbol() == '.':

            self.tokenizer.advance()

            # subroutine name
            static_method_name = self.tokenizer.identifier()
            self.tokenizer.advance()

            self.check_required_token(self.tokenizer.key_word(), '(')
            self.tokenizer.advance()  # )

            n_args = self.compile_expression_list()

            self.check_required_token(self.tokenizer.symbol(), ')')
            self.tokenizer.advance()

            self.vm_writer.write_call(name='{class_name}.{function_name}'
                                      .format(class_name=previous_token,
                                              function_name=static_method_name), n_args=n_args)

    @staticmethod
    def check_required_token(token, required_token):
        if token != required_token:
            raise ValueError('except to find "{}" but found {}'.format(required_token, token))

    @staticmethod
    def convert_kind_to_vm_keyword(type_):
        if type_ == 'static':
            return 'static'
        elif type_ == 'field':
            return 'this'
        elif type_ == 'var':
            return 'local'
        elif type_ == 'argument':
            return 'argument'


if __name__ == '__main__':

    cur_dir = os.getcwd()
    file_path = sys.argv[1]

    if '.jack' in file_path:
        tokenizer = JackTokenizer(file_path)
        st = SymbolTable()
        vm_writer = VMWriter(file_path)
        compilation_engine = CompilationEngine(tokenizer, file_path.split('.')[0] + '.vm', st, vm_writer)
        compilation_engine.compile()
    else:
        files = os.listdir(file_path)
        files = [file for file in files if '.jack' in file]
        os.chdir(file_path)
        for file in files:
            tokenizer = JackTokenizer(file)
            st = SymbolTable()
            vm_writer = VMWriter(file.split('.')[0] + '.vm')
            compilation_engine = CompilationEngine(tokenizer, file.split('.')[0] + '.vm', st, vm_writer)
            compilation_engine.compile()
        os.chdir(cur_dir)
