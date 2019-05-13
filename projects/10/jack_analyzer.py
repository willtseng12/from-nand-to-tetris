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

    def __init__(self):
        self.jack_content = self._load_file('ArrayTest/Main.jack')
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
            self.current_token_type = 'SYMBOL'
            self.current_pointer += 1
            return

        # string literal case
        if current_char == '"':  # start of a literal
            self.current_token_type = 'STRING_CONSTANT'

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
            self.current_token_type = 'INTEGER_CONSTANT'

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
            self.current_token_type = 'KEYWORD'
        else:
            self.current_token_type = 'IDENTIFIER'

    def token_type(self):
        return self.current_token_type

    def key_word(self):
        return self.JACK_KEYWORD[self.current_token]

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
            return ' '.join(content_list)

    @staticmethod
    def is_int_value(s):
        try:
            int(s)
        except ValueError:
            return False
        return True


if __name__ == '__main__':
    tokenizer = JackTokenizer()
    while tokenizer.has_more_tokens():
        tokenizer.advance()
        print(tokenizer.current_token)
        if tokenizer.token_type() == 'KEYWORD':
            print(tokenizer.key_word())
        else:
            print(tokenizer.token_type())

