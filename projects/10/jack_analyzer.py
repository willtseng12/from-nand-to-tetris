class JackTokenizer:

    def __init__(self, file_path):
        self.jack_content = self._load_file(file_path)
        self.current_pointer = 0
        self.current_token = None
        self.current_token_type = None

    def has_more_tokens(self):
        return self.current_pointer < len(self.jack_content)

    def advance(self):
        if not self.has_more_tokens():
            raise ValueError('No more content to parse')

        self.current_token = ''
        current_char = self.jack_content[self.current_pointer]
        while current_char == ' ':
            self.current_pointer += 1
            current_char = self.jack_content[self.current_pointer]

        # symbol case
        if current_char in self.jack_symbol():
            self.current_token = current_char
            self.current_token_type = 'symbol'
            self.current_pointer += 1
            return

        # string literal case
        if current_char == '"':  # start of a literal
            self.current_token_type = 'stringConstant'

            while True:
                self.current_pointer += 1
                current_char = self.jack_content[self.current_pointer]
                if current_char == '"':
                    break
                else:
                    self.current_token = self.current_token + current_char
            self.current_pointer += 1
            return

        # int case
        if self.is_int_value(current_char):
            self.current_token_type = 'integerConstant'

            while self.current_pointer < len(self.jack_content):
                current_char = self.jack_content[self.current_pointer]
                if self.is_int_value(current_char):
                    self.current_token = self.current_token + current_char
                else:
                    break
                self.current_pointer += 1
            return

        # identifier or keyword case
        while (current_char != ' ' and
               current_char not in self.jack_symbol() and
               self.current_pointer < len(self.jack_content)):
            self.current_token = self.current_token + current_char
            self.current_pointer += 1
            current_char = self.jack_content[self.current_pointer]

        if self.current_token in self.jack_keyword():
            self.current_token_type = 'keyword'
        else:
            self.current_token_type = 'identifier'

    def token_type(self):
        return self.current_token_type

    def key_word(self):
        return self.current_token

    def symbol(self):
        return self.current_token

    def identifier(self):
        return self.current_token

    def int_val(self):
        return int(self.current_token)

    def string_val(self):
        return self.current_token

    @staticmethod
    def jack_operator():
        return {'+', '-', '*', '/', '&', '|', '<', '>', '='}

    @staticmethod
    def convert_operator(symbol):
        return {'>': '&gt;',
                '<': '&lt;',
                '&': '&amp;'}[symbol]

    @staticmethod
    def jack_keyword():
        return {'class': 'CLASS',
                'constructor': 'CONSTRUCTOR',
                'function': 'FUNCTION',
                'method': 'METHOD',
                'field': 'FIELD',
                'static': 'STATIC',
                'var': 'VAR',
                'int': 'INT',
                'char': 'CHAR',
                'boolean': 'BOOLEAN',
                'void': 'VOID',
                'true': 'TRUE',
                'false': 'FALSE',
                'null': 'NULL',
                'this': 'THIS',
                'let': 'LET',
                'do': 'DO',
                'if': 'IF',
                'else': 'ELSE',
                'while': 'WHILE',
                'return': 'RETURN'}

    @staticmethod
    def jack_symbol():
        return {'{',
                '}',
                '(',
                ')',
                '[',
                ']',
                '.',
                ',',
                ';',
                '+',
                '-',
                '*',
                '/',
                '&',
                '|',
                '<',
                '>',
                '=',
                '~'}

    @staticmethod
    def _load_file(jack_filename):
        with open(jack_filename, 'r') as f:
            content = f.read()
            content_list = content.split('\n')  # get line by line
            content_list = [l.strip() for l in content_list]
            content_list = [l for l in content_list if not ((l.startswith('/**')) or
                                                            l.endswith('*/') or
                                                            l.startswith('//') or
                                                            l.startswith('*') or
                                                            l == '')
                            ]
            content_list = [l.split('//')[0] for l in content_list]  # get rid of inline comment
            return ' '.join(content_list)

    @staticmethod
    def is_int_value(s):
        try:
            int(s)
        except ValueError:
            return False
        return True


class CompilationEngine:

    def __init__(self, tokenizer, out_file_name):
        self.tokenizer = tokenizer
        self.out_file_name = out_file_name
        self.encounter_empty_expression_list = False
        self.indent = ''
        self.writer = open(out_file_name, 'w')

    def compile(self):
        self.compile_class()

    def compile_class(self):
        self.tokenizer.advance()

        self.writer.write('<class>\n')
        self.updent()

        self.check_required_token(self.tokenizer.key_word(), 'class')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))

        self.tokenizer.advance()
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                type=self.tokenizer.token_type()))

        self.tokenizer.advance()
        self.check_required_token(self.tokenizer.key_word(), '{')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()
        while self.tokenizer.symbol() in ('field', 'static'):
            self.compile_class_var_dec()
        while self.tokenizer.key_word() in ('constructor', 'function', 'method'):
            self.compile_subroutine_dec()

        self.check_required_token(self.tokenizer.key_word(), '}')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.downdent()
        self.writer.write('</class>\n')

    def compile_class_var_dec(self):

        self.writer.write(self.indent + '<classVarDec>\n')
        self.updent()
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                type=self.tokenizer.token_type()))

        self.tokenizer.advance()

        while self.tokenizer.symbol() == ',':
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        # ;
        self.check_required_token(self.tokenizer.symbol(), ';')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</classVarDec>\n')

    def compile_subroutine_dec(self):

        self.writer.write(self.indent + '<subroutineDec>\n')
        self.updent()
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()
        # return type
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # subroutine name
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.check_required_token(self.tokenizer.key_word(), '(')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_parameter_list()

        self.check_required_token(self.tokenizer.key_word(), ')')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_subroutine_body()

        self.downdent()
        self.writer.write(self.indent + '</subroutineDec>\n')

    def compile_parameter_list(self):
        self.writer.write(self.indent + '<parameterList>\n')
        self.updent()
        while self.tokenizer.symbol() != ')':

            # param type
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            # param name
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            if self.tokenizer.symbol() == ',':
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</parameterList>\n')

    def compile_subroutine_body(self):
        self.writer.write(self.indent + '<subroutineBody>\n')
        self.updent()

        # {
        self.check_required_token(self.tokenizer.symbol(), '{')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()
        while self.tokenizer.symbol() == 'var':
            self.compile_var_dec()
        self.compile_statements()

        # }
        self.check_required_token(self.tokenizer.symbol(), '}')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</subroutineBody>\n')

    def compile_var_dec(self):

        self.writer.write(self.indent + '<varDec>\n')
        self.updent()

        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # local variable type
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))

        self.tokenizer.advance()

        # local variable name
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # potentially additional variable name
        while self.tokenizer.symbol() == ',':
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        # ;
        self.check_required_token(self.tokenizer.symbol(), ';')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</varDec>\n')

    def compile_statements(self):
        self.writer.write(self.indent + '<statements>\n')
        self.updent()
        while self.tokenizer.key_word() in ('let', 'if', 'while', 'do', 'return'):
            if self.tokenizer.key_word() == 'let':
                self.compile_let()

            elif self.tokenizer.key_word() == 'do':
                self.compile_do()

            elif self.tokenizer.key_word() == 'return':
                self.compile_return()

            elif self.tokenizer.key_word() == 'if':
                self.compile_if()

            elif self.tokenizer.key_word() == 'while':
                self.compile_while()

        self.downdent()
        self.writer.write(self.indent + '</statements>\n')

    def compile_do(self):
        self.writer.write(self.indent + '<doStatement>\n')
        self.updent()

        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        current_token, current_token_type = self.tokenizer.identifier(), self.tokenizer.token_type()
        self.tokenizer.advance()

        self._compile_subroutine_call(previous_token=current_token,
                                      previous_token_type=current_token_type)

        # ;
        self.check_required_token(self.tokenizer.symbol(), ';')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</doStatement>\n')

    def compile_let(self):
        self.writer.write(self.indent + '<letStatement>\n')
        self.updent()

        # let
        self.check_required_token(self.tokenizer.key_word(), 'let')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # identifier
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # array case
        if self.tokenizer.symbol() == '[':
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.compile_expression()

            self.check_required_token(self.tokenizer.key_word(), ']')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        # =
        self.check_required_token(self.tokenizer.key_word(), '=')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # rhs equality
        self.compile_expression()

        # ;
        self.check_required_token(self.tokenizer.key_word(), ';')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</letStatement>\n')

    def compile_while(self):
        self.writer.write(self.indent + '<whileStatement>\n')
        self.updent()

        # while
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # (
        self.check_required_token(self.tokenizer.key_word(), '(')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_expression()

        # )
        self.check_required_token(self.tokenizer.key_word(), ')')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # {
        self.check_required_token(self.tokenizer.key_word(), '{')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_statements()

        # }
        self.check_required_token(self.tokenizer.key_word(), '}')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</whileStatement>\n')

    def compile_return(self):
        self.writer.write(self.indent + '<returnStatement>\n')
        self.updent()

        # return
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        if self.tokenizer.symbol() != ';':
            self.compile_expression()

            # ;
            self.check_required_token(self.tokenizer.key_word(), ';')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        else:
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</returnStatement>\n')

    def compile_if(self):
        self.writer.write(self.indent + '<ifStatement>\n')
        self.updent()

        # if
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.key_word(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.check_required_token(self.tokenizer.key_word(), '(')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_expression()

        self.check_required_token(self.tokenizer.key_word(), ')')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # {

        self.check_required_token(self.tokenizer.key_word(), '{')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        self.compile_statements()

        self.check_required_token(self.tokenizer.key_word(), '}')
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                type=self.tokenizer.token_type()))
        self.tokenizer.advance()

        # else?
        if self.tokenizer.key_word() == 'else':
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.check_required_token(self.tokenizer.key_word(), '{')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.compile_statements()

            self.check_required_token(self.tokenizer.key_word(), '}')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        self.downdent()
        self.writer.write(self.indent + '</ifStatement>\n')

    def compile_expression(self):

        # case when expression list is suppose to be empty we dont want to print the expression tag
        no_expression = self.tokenizer.symbol() == ')'

        if not no_expression:
            self.writer.write(self.indent + '<expression>\n')
            self.updent()

        self.compile_term()

        # (operator term)*
        while self.tokenizer.symbol() in self.tokenizer.jack_operator():
            if self.tokenizer.symbol() in ('>', '<', '&'):
                converted_symbol = JackTokenizer.convert_operator(self.tokenizer.symbol())
            else:
                converted_symbol = self.tokenizer.symbol()
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=converted_symbol,
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.compile_term()

        if not no_expression:
            self.downdent()
            self.writer.write(self.indent + '</expression>\n')

    def compile_term(self):

        # case when expression list is empty
        if self.tokenizer.symbol() != ')':
            self.writer.write(self.indent + '<term>\n')
            self.updent()

        # "(" expression ")" case
        if self.tokenizer.symbol() == '(':
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()
            self.compile_expression()
            self.check_required_token(self.tokenizer.key_word(), ')')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

        # unary op term case
        elif self.tokenizer.symbol() in ('-', '~'):
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()
            self.compile_term()

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
                # array var name
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=current_token,
                                                                        type=current_token_type))

                # [
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()

                self.compile_expression()

                # ]
                self.check_required_token(self.tokenizer.key_word(), ']')
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()

            # Integer constant
            elif JackTokenizer.is_int_value(current_token):
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=current_token,
                                                                        type=current_token_type))
            elif current_token == '"':

                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()
                # check for closing string quote, ignore it
                self.check_required_token(self.tokenizer.symbol(), '"')
                self.tokenizer.advance()

            # keyword constant
            elif current_token in ('true', 'false', 'null', 'this'):
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=current_token,
                                                                        type=current_token_type))
            # var name
            elif current_token != ')':
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=current_token,
                                                                        type=current_token_type))
            elif current_token == ')':
                self.encounter_empty_expression_list = True
                return

        self.downdent()
        self.writer.write(self.indent + '</term>\n')

    def compile_expression_list(self):
        self.writer.write(self.indent + '<expressionList>\n')
        self.updent()

        self.compile_expression()

        while self.tokenizer.symbol() == ',':
            # evidently false if there are more
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()
            self.compile_expression()

        self.downdent()
        self.writer.write(self.indent + '</expressionList>\n')

    def _compile_subroutine_call(self, previous_token, previous_token_type):
        # identifier either class name or subroutine name
        self.writer.write(self.indent +
                          '<{type}> {token} </{type}>\n'.format(token=previous_token,
                                                                type=previous_token_type))

        # method
        if self.tokenizer.symbol() == '(':

            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.compile_expression_list()

            if self.encounter_empty_expression_list:
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=')',
                                                                        type='symbol'))
                self.encounter_empty_expression_list = False

            else:
                self.check_required_token(self.tokenizer.key_word(), ')')
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()

        # static method
        elif self.tokenizer.symbol() == '.':

            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            # subroutine name
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.identifier(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.check_required_token(self.tokenizer.key_word(), '(')
            self.writer.write(self.indent +
                              '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                    type=self.tokenizer.token_type()))
            self.tokenizer.advance()

            self.compile_expression_list()

            if self.encounter_empty_expression_list:
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=')',
                                                                        type='symbol'))
                self.encounter_empty_expression_list = False
            else:
                self.check_required_token(self.tokenizer.key_word(), ')')
                self.writer.write(self.indent +
                                  '<{type}> {token} </{type}>\n'.format(token=self.tokenizer.symbol(),
                                                                        type=self.tokenizer.token_type()))
                self.tokenizer.advance()

    @staticmethod
    def check_required_token(token, required_token):
        if token != required_token:
            raise ValueError('except to find "{}" but found {}'.format(required_token, token))

    def updent(self):
        self.indent = self.indent + '  '

    def downdent(self):
        self.indent = self.indent[:-2]


if __name__ == '__main__':
    import sys
    import os

    cur_dir = os.getcwd()
    file_path = sys.argv[1]

    if '.jack' in file_path:
        tokenizer = JackTokenizer(file_path)
        compilation_engine = CompilationEngine(tokenizer, file_path.split('.')[0] + '.xml')
        compilation_engine.compile()
    else:
        files = os.listdir(file_path)
        files = [file for file in files if '.jack' in file]
        os.chdir(file_path)
        for file in files:
            tokenizer = JackTokenizer(file)
            compilation_engine = CompilationEngine(tokenizer, file.split('.')[0] + '.xml')
            compilation_engine.compile()
        os.chdir(cur_dir)
