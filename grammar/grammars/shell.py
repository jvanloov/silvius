from ast import AST


class ShellCmdMixin(object):

    def __init__(self, *args, **kwargs):
        # register this subgrammar on the main grammar in CoreParser
        self.add_subgrammar(["shell_cmd"])

    def p_shell_cmd(self, args):
        '''
            shell_cmd ::= shell_name change
            shell_cmd ::= shell_name list
        '''
        value = {
            'change' : 'cd ',
            'list':    'ls -la '
        }
        sequence = []
        for ch in value[args[1].type]:
            if ch == ' ':
                sequence.append(AST("raw_char", [ 'space'] ))
            elif ch == '-':
                sequence.append(AST("raw_char", [ 'minus'] ))
            else:
                sequence.append(AST("char", [ ch ]))
        return AST("chain", None, sequence)

    def p_shell_name(self, args):
        '''
            shell_name ::= cheryl
            shell_name ::= sherrill
        '''
        return args[0]
