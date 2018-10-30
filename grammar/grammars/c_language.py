from ast import AST


class C_LanguageMixin(object):

    def __init__(self, *args, **kwargs):
        # register this subgrammar on the main grammar in CoreParser
        self.add_subgrammar(["c_language"])

    def p_c_language(self, args):
        '''
            c_language ::= c_language_cmd and
            c_language ::= c_language_cmd block
        '''
        sequence = []
        if args[1].type == 'and':
            sequence.append(AST("raw_char", [ 'semicolon'] ))
        elif args[1].type == 'block':
            sequence.append(AST('raw_char', [ 'braceleft'] ))
            sequence.append(AST('raw_char', [ 'braceright' ] ))
        return AST("chain", None, sequence)

    def p_c_language_cmd(self, args):
        '''
            c_language_cmd ::= c
        '''
        return args[0]
