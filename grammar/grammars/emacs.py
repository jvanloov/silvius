from ast import AST


class EmacsMixin(object):

    def __init__(self, *args, **kwargs):
        # register this subgrammar on the main grammar in CoreParser
        self.add_subgrammar(["emacs_cmd"])

    def p_emacs_cmd(self, args):
        '''
            emacs_cmd ::= emacs_name scratch
            emacs_cmd ::= emacs_name function
            emacs_cmd ::= emacs_name point
            emacs_cmd ::= emacs_name remember
            emacs_cmd ::= emacs_name save
            emacs_cmd ::= emacs_name switch
            emacs_cmd ::= emacs_name window
            emacs_cmd ::= emacs_name split
            emacs_cmd ::= emacs_name merge
            emacs_cmd ::= emacs_name cancel
            emacs_cmd ::= emacs_name yankee
            emacs_cmd ::= emacs_name center
            emacs_cmd ::= emacs_name many
            emacs_cmd ::= emacs_name grab
            emacs_cmd ::= emacs_name begin
            emacs_cmd ::= emacs_name and
            emacs_cmd ::= emacs_name swallow
            emacs_cmd ::= emacs_name close
            emacs_cmd ::= emacs_name search
            emacs_cmd ::= emacs_name clear
            emacs_cmd ::= emacs_name disappear
            emacs_cmd ::= emacs_name go
        
            emacs_cmd ::= emacs_name five
            emacs_cmd ::= emacs_name ten
            emacs_cmd ::= emacs_name fifteen
            emacs_cmd ::= emacs_name twenty

            emacs_cmd ::= emacs_name beautify
            emacs_cmd ::= emacs_name refresh
       '''
        sequence = []
        if args[1].type == 'scratch':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST("char", [ 'u'] ))
        elif args[1].type == 'function':
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST('char', [ 'x' ] ))
        elif args[1].type == 'point':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("raw_char", [ 'space'] ) ] ))
        elif args[1].type == 'remember':
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST('char', [ 'w' ] ))
        elif args[1].type == 'save':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 's'] ) ] ))
        elif args[1].type == 'switch':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST("char", [ 'b'] ))
        elif args[1].type == 'window':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST("char", [ 'o'] ))
        elif args[1].type == 'split':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('char', [ '2'] ))
        elif args[1].type == 'merge':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('char', [ '1'] ))
        elif args[1].type == 'cancel':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'g'] ) ] ))
        elif args[1].type == 'yankee':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'y'] ) ] ))
        elif args[1].type == 'center':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'l'] ) ] ))
        elif args[1].type == 'many':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'u'] ) ] ))
        elif args[1].type == 'grab':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'w'] ) ] ))
        elif args[1].type == 'begin':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'a'] ) ] ))
        elif args[1].type == 'and':  # 'end'
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'e'] ) ] ))
        elif args[1].type == 'swallow':
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST("char", [ 'd'] ))
        elif args[1].type == 'close':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('char', [ 'k'] ))
        elif args[1].type == 'search':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 's'] ) ] ))
        elif args[1].type == 'clear':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'k'] ) ] ))
        elif args[1].type == 'disappear':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'w'] ) ] ))
        elif args[1].type == 'go':
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST("char", [ 'g'] ))
            sequence.append(AST("char", [ 'g'] ))
        elif args[1].type == 'five':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'u'] ) ] ))
            sequence.append(AST("raw_char", [ '5'] ))
        elif args[1].type == 'ten':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'u'] ) ] ))
            sequence.append(AST("raw_char", [ '1'] ))
            sequence.append(AST("raw_char", [ '0'] ))
        elif args[1].type == 'fifteen':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'u'] ) ] ))
            sequence.append(AST("raw_char", [ '1'] ))
            sequence.append(AST("raw_char", [ '5'] ))
        elif args[1].type == 'twenty':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'u'] ) ] ))
            sequence.append(AST("raw_char", [ '2'] ))
            sequence.append(AST("raw_char", [ '0'] ))
        elif args[1].type == 'beautify':
            #sequence.append(AST('mod_plus_key', [ 'ctrl', 'alt' ], [ AST("raw_char", [ 'backslash'] ) ] ))
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST('char', [ 'x' ] ))
            sequence.append(AST('sequence', [ 'inde-reg' ] ))   # will be expanded to indent-region by the "tab"
            sequence.append(AST('raw_char', [ 'Tab'] ))
            sequence.append(AST('raw_char', [ 'Return'] ))
        elif args[1].type == 'refresh':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'v'] ) ] ))
            sequence.append(AST('raw_char', [ 'Return'] ))
        return AST("chain", None, sequence)

    def p_emacs_name(self, args):
        '''
            emacs_name ::= last
        '''
        return args[0]
