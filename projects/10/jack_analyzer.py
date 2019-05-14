class JackTokenizer:
    JACK_SYMBOL = {'{',
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

    JACK_KEYWORD = {'class': 'CLASS',
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
        if current_char in self.JACK_SYMBOL:
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
               current_char not in self.JACK_SYMBOL and
               self.current_pointer < len(self.jack_content)):
            self.current_token = self.current_token + current_char
            self.current_pointer += 1
            current_char = self.jack_content[self.current_pointer]

        if self.current_token in self.JACK_KEYWORD:
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
        self.compile_class_var_dec()
        self.compile_subroutine_dec()

    def compile_class_var_dec(self):
        self.tokenizer.advance()

        while self.tokenizer.symbol() in ('field', 'static'):
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
        while self.tokenizer.key_word() in ('constructor', 'function', 'method'):
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
        self.compile_var_dec()

    def compile_var_dec(self):
        while self.tokenizer.symbol() == 'var':
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
        pass

    def compile_do(self):
        pass

    def compile_let(self):
        pass

    def compile_while(self):
        pass

    def compile_return(self):
        pass

    def compile_if(self):
        pass

    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass

    @staticmethod
    def check_required_token(token, required_token):
        if token != required_token:
            raise ValueError('except to find "{}" but found {}'.format(required_token, token))

    def updent(self):
        self.indent = self.indent + '  '

    def downdent(self):
        self.indent = self.indent[:-2]


if __name__ == '__main__':
    tokenizer = JackTokenizer('ExpressionLessSquare/Main.jack')
    compilation_engine = CompilationEngine(tokenizer, 'test_name.xml')
    compilation_engine.compile()
    # while tokenizer.has_more_tokens():
    #     tokenizer.advance()
    #     print(tokenizer.identifier())
