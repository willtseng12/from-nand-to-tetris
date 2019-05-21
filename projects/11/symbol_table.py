class SymbolTable:

    def __init__(self):
        self.class_st = {}
        self.subroutine_st = {}
        self.static_index = 0
        self.field_index = 0
        self.argument_index = 0
        self.var_index = 0

    def define(self, name, type, kind):
        if kind == 'static':
            self.class_st[name] = [type, kind, self.static_index]
            self.static_index += 1
        elif kind == 'field':
            self.class_st[name] = [type, kind, self.field_index]
            self.field_index += 1
        elif kind == 'var':
            self.subroutine_st[name] = [type, kind, self.var_index]
            self.var_index += 1
        elif kind == 'argument':
            self.subroutine_st[name] = [type, kind, self.argument_index]
            self.argument_index += 1

    def start_sub_routine(self):
        self.subroutine_st.clear()
        self.argument_index = 0
        self.var_index = 0

    def index_of(self, name):
        if name in self.subroutine_st:
            return self.subroutine_st[name][2]
        elif name in self.class_st:
            return self.class_st[name][2]
        else:
            return None

    def kind_of(self, name):
        if name in self.subroutine_st:
            return self.subroutine_st[name][1]
        elif name in self.class_st:
            return self.class_st[name][1]
        else:
            return None

    def type_of(self, name):
        if name in self.subroutine_st:
            return self.subroutine_st[name][0]
        elif name in self.class_st:
            return self.class_st[name][0]
        else:
            return None

    def var_count(self, kind):
        assert kind in ('static', 'field', 'var', 'argument')

        if kind == 'static':
            return self.static_index
        elif kind == 'field':
            return self.field_index
        elif kind == 'var':
            return self.var_index
        else:
            return self.argument_index
