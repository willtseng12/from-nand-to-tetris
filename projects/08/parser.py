class Parser:
    COMMANDS = {
        'add': 'C_ARITHMETIC',
        'sub': 'C_ARITHMETIC',
        'neg': 'C_ARITHMETIC',
        'eq': 'C_ARITHMETIC',
        'gt': 'C_ARITHMETIC',
        'lt': 'C_ARITHMETIC',
        'and': 'C_ARITHMETIC',
        'or': 'C_ARITHMETIC',
        'not': 'C_ARITHMETIC',
        'push': 'C_PUSH',
        'pop': 'C_POP',
        'label': 'C_LABEL',
        'goto': 'C_GOTO',
        'if-goto': 'C_IF',
        'function': 'C_FUNCTION',
        'return': 'C_RETURN',
        'call': 'C_CALL'
    }

    def __init__(self, input_path):
        self.i = 0
        self.commands = self._get_commands(input_path)

    def has_more_commands(self):
        """Return whether there are more VM commands left to be translated"""
        return self.i < len(self.commands)

    def advance(self):
        """Return the next dictionary parsed VM command"""
        if not self.has_more_commands():
            raise ValueError('No more commands')
        commands = self.commands[self.i].split()
        command_type = self.COMMANDS.get(commands[0])
        self.i += 1
        if command_type == 'C_ARITHMETIC':  # arithmetic
            return {'command_type': command_type, 'command': commands[0]}  # arithmetic/logical command
        elif command_type in ('C_LABEL', 'C_GOTO', 'C_IF'):
            return {'command_type': command_type, 'label': commands[1]}  # program control command
        elif command_type == 'C_FUNCTION':
            return {'command_type': command_type, 'function_name': commands[1],
                    'n_vars': commands[2]}
        elif command_type == 'C_CALL':
            return {'command_type': command_type, 'function_name': commands[1],
                    'n_args': commands[2]}
        elif command_type == 'C_RETURN':
            return {'command_type': command_type}
        else:  # push / pop
            return {'command_type': command_type,
                    'segment': commands[1],
                    'index': commands[2]}  # push/pull, segment, location address

    @staticmethod
    def _get_commands(path):
        commands = []
        with open(path, 'r') as f:
            file = f.read().split('\n')
            for line in file:
                l = line.strip()
                if l.startswith('//') or l == '':
                    continue
                else:
                    commands.append(l.split('//')[0].strip())
        return commands
