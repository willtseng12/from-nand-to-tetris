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
