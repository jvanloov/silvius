from ast import AST
from scan import Token

class MovementEditingMixin(object):

    def __init__(self, *args, **kwargs):
        # register this subgrammar on the main grammar in CoreParser
        self.add_subgrammar(["movement", "editing"])

    def p_movement(self, args):
        '''
            movement ::= up     repeat
            movement ::= down   repeat
            movement ::= left   repeat
            movement ::= right  repeat
            movement ::= back   repeat
            movement ::= scroll repeat
            movement ::= jump_cmd left  repeat
            movement ::= jump_cmd right repeat
        '''
        if args[0].type == 'jump':
            # TODO: this is Emacs specific; refactor?
            movement = AST('chain', None, [
                AST("raw_char", [ 'Escape' ] ),
                AST("movement", [ Token(args[1].type) ] )
                ])
            if len(args) > 2 and args[2] != None:
                args[0] = AST('repeat', [ args[2] ], [ movement ] )
            else:
                args[0] = movement
            return args[0]
        elif args[1] != None:
            movement = args[0]
            if movement.type == "back":
                movement = Token("pageup")
            elif movement.type == "scroll":
                movement = Token("pagedown")
            return AST('repeat', [ args[1] ], [
                AST('movement', [ movement ])
            ])
        else:
            movement = args[0]
            if movement.type == "back":
                movement = Token("pageup")
            elif movement.type == "scroll":
                movement = Token("pagedown")
            return AST('movement', [ movement ])

    def p_jump_cmd(self, args):
        '''
            jump_cmd ::= jump
        '''
        return AST('jump')

    def p_editing(self, args):
        '''
            editing ::= slap        repeat
            editing ::= scratch     repeat
        '''
        value = {
            'slap'  : 'Return',
            'scratch': 'BackSpace'
        }
        if args[1] != None:
            return AST('repeat', [ args[1] ], [
                AST('raw_char', [ value[args[0].type] ])
            ])
        else:
            return AST('raw_char', [ value[args[0].type] ])

