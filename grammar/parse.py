# Parser, based on John Aycock's SPARK examples

from copy import deepcopy
from spark import GenericParser
from spark import GenericASTBuilder
from ast import AST
from scan import Token

class GrammaticalError(Exception):
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string

class CoreParser(GenericParser):

    terminals = []

    def __init__(self, start):
        # initialize and set up the grammar rules
        GenericParser.__init__(self, start)
        # after the "base" initialization, collect all terminals
        visited = {}
        self.find_terminals(self.rules, visited, 'START', self.terminals)
        self.terminals = list(set(self.terminals))  # remove duplicates
        # add terminal rules if needed
        self.install_terminal_rules()
        # re-initialize the parser rules
        GenericParser.__init__(self, start)

    # collect all terminals from the grammar rules
    def find_terminals(self, rules, visited, which, found):
        if which in visited: return
        visited[which] = 1
        for r in rules[which]:
            (name, tokens) = r
            for t in tokens:
                if t in rules:
                    self.find_terminals(rules, visited, t, found)
                elif t != 'END' and t != 'ANY' and t != '|-':
                    found.append(t)

    # In our grammar, the token type ANY does not match any of the other
    # token types. In some cases, this is not the desired behavior, e.g. for
    # "word <word>" you want <word> to be able to be "five" or "sentence" or
    # any other word that may have been used as a terminal in the grammar.
    # This becomes more of an issue as you add macros, and more words become
    # reserved.
    # We can work around this limitation by adding rules for terminals
    # that we want to allow; however, with many terminals this will
    # quickly become infeasible.
    # The function and function decorator below work together to automate this.
    # (The decorator is needed to modify the docstring programmatically.)
    # We rely on the fact that in main.py, we already collect a list of
    # terminals (using find_terminals()). This does mean, however, that we
    # have to instantiate the parser twice: first in "basic" form, which is
    # used to collect the terminals, and then again in "decorated" form, where
    # we automatically add the desired terminal rules.

    def install_terminal_rules(self):
        # if we have a list of terminals available: walk all rules, and see
        # if they were annotated with @add_rules_for_terminals. If so, we add
        # new rules based on the template for that rule and the terminals.
        if len(self.terminals) > 0:
            for item in CoreParser.__dict__:
                if item.startswith("p_"):
                    function = CoreParser.__dict__[item]
                    try:
                        # this will trigger an AttributeError
                        # for functions that were not annotated:
                        template = function._rule_template
                        exclusions = function._exclusions
                        for kw in set(self.terminals) - set(exclusions):
                            function.__doc__ += \
                                (template.format(kw) + "\n")
                    except AttributeError:
                        pass

    # function decorator: adding @add_rules_for_termination("<rule_template>")
    # before a function declaration will add the given rule template
    # as a new attribute to the function.
    # This is used to signal that for this function, we have to add a new rule
    # for each terminal, so that the terminal can be used in the spoken text.
    def add_rules_for_terminals(rule_template, exclusions=[]):
        def add_attrs(func):
            func._rule_template = rule_template
            func._exclusions = exclusions
            return func
        return add_attrs


    def typestring(self, token):
        return token.type

    def error(self, token):
        raise GrammaticalError(
            "Unexpected token `%s' (word number %d)" % (token, token.wordno))

    def p_chained_commands(self, args):
        '''
            chained_commands ::= single_command
            chained_commands ::= single_command chained_commands
        '''
        if(len(args) == 1):
            return AST('chain', None, [ args[0] ])
        else:
            args[1].children.insert(0, args[0])
            return args[1]

    def p_single_command(self, args):
        '''
            single_command ::= letter
            single_command ::= sky_letter
            single_command ::= number_rule
            single_command ::= movement
            single_command ::= character
            single_command ::= editing
            single_command ::= modifiers
            single_command ::= english
            single_command ::= word_sentence
            single_command ::= word_phrase
            single_command ::= word_camel
            single_command ::= shell_cmd
            single_command ::= emacs_cmd
        '''
        return args[0]

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
    

    def p_repeat(self, args):
        '''
            repeat ::=
            repeat ::= number_set
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None

    small_numbers = {
        'zero'      : 0,
        'one'       : 1,
        'two'       : 2,
        'three'     : 3,
        'four'      : 4,
        'five'      : 5,
        'six'       : 6,
        'seven'     : 7,
        'eight'     : 8,
        'nine'      : 9,
        'ten'       : 10,
        'eleven'    : 11,
        'twelve'    : 12,
        'thirteen'  : 13,
        'fourteen'  : 14,
        'fifteen'   : 15,
        'sixteen'   : 16,
        'seventeen' : 17,
        'eighteen'  : 18,
        'nineteen'  : 19,

        # sadly, kaldi often recognizes these by accident
        'to'        : 2,
        'for'       : 4,
    }
    def p_number_rule(self, args):
        '''
            number_rule ::= number number_set
            number_rule ::= number thousand_number_set
            number_rule ::= number million_number_set
            number_rule ::= number billion_number_set
        '''
        return AST('sequence', [ str(args[1]) ])
    def p_number_set(self, args):
        '''
            number_set ::= _firstnumbers
            number_set ::= _tens
            number_set ::= _tens _ones
            number_set ::= _hundreds
            number_set ::= _hundreds _firstnumbers
            number_set ::= _hundreds _tens
            number_set ::= _hundreds _tens _ones
        '''
        return sum(args)
    def p__ones(self, args):
        '''
            _ones ::= one
            _ones ::= two
            _ones ::= three
            _ones ::= four
            _ones ::= five
            _ones ::= six
            _ones ::= seven
            _ones ::= eight
            _ones ::= nine
            _ones ::= to
            _ones ::= for
        '''
        return self.small_numbers[args[0].type]
    def p__firstnumbers(self, args):
        '''
            _firstnumbers ::= zero
            _firstnumbers ::= one
            _firstnumbers ::= two
            _firstnumbers ::= three
            _firstnumbers ::= four
            _firstnumbers ::= five
            _firstnumbers ::= six
            _firstnumbers ::= seven
            _firstnumbers ::= eight
            _firstnumbers ::= nine
            _firstnumbers ::= ten
            _firstnumbers ::= eleven
            _firstnumbers ::= twelve
            _firstnumbers ::= thirteen
            _firstnumbers ::= fourteen
            _firstnumbers ::= fifteen
            _firstnumbers ::= sixteen
            _firstnumbers ::= seventeen
            _firstnumbers ::= eighteen
            _firstnumbers ::= nineteen
            _firstnumbers ::= to
            _firstnumbers ::= for
        '''
        return self.small_numbers[args[0].type]
    def p__tens(self, args):
        '''
            _tens ::= twenty
            _tens ::= thirty
            _tens ::= forty
            _tens ::= fifty
            _tens ::= sixty
            _tens ::= seventy
            _tens ::= eighty
            _tens ::= ninety
        '''
        value = {
            'twenty'   : 20,
            'thirty'   : 30,
            'forty'    : 40,
            'fifty'    : 50,
            'sixty'    : 60,
            'seventy'  : 70,
            'eighty'   : 80,
            'ninety'   : 90
        }
        return value[args[0].type]
    def p__hundreds(self, args):
        '''
            _hundreds ::= _ones hundred
        '''
        return args[0] * 100
    def p_thousand_number_set(self, args):
        '''
            thousand_number_set ::= number_set thousand
            thousand_number_set ::= number_set thousand number_set
        '''
        total = args[0] * 1000
        if len(args) > 2: total += args[2]
        return total
    def p_million_number_set(self, args):
        '''
            million_number_set ::= number_set million
            million_number_set ::= number_set million number_set
            million_number_set ::= number_set million thousand_number_set
        '''
        total = args[0] * 1000000
        if len(args) > 2: total += args[2]
        return total
    def p_billion_number_set(self, args):
        '''
            billion_number_set ::= number_set billion
            billion_number_set ::= number_set billion number_set
            billion_number_set ::= number_set billion thousand_number_set
            billion_number_set ::= number_set billion million_number_set
        '''
        total = args[0] * 1000000000
        if len(args) > 2: total += args[2]
        return total

    def p_sky_letter(self, args):
        '''
            sky_letter ::= sky letter
        '''
        ast = args[1]
        ast.meta[0] = ast.meta[0].upper()
        return ast

    def p_letter(self, args):
        '''
            letter ::= arch
            letter ::= bravo
            letter ::= charlie
            letter ::= delta
            letter ::= eco
            letter ::= echo
            letter ::= fox
            letter ::= greece
            letter ::= hotel
            letter ::= india
            letter ::= julia
            letter ::= kilo
            letter ::= line
            letter ::= mike
            letter ::= november
            letter ::= oscar
            letter ::= papa
            letter ::= queen
            letter ::= romeo
            letter ::= sierra
            letter ::= tango
            letter ::= uniform
            letter ::= victor
            letter ::= whiskey
            letter ::= whisky
            letter ::= xray
            letter ::= expert
            letter ::= yankee
            letter ::= zulu
        '''
        if(args[0].type == 'expert'): args[0].type = 'x'
        return AST('char', [ args[0].type[0] ])

    def p_character(self, args):
        '''
            character ::= act
            character ::= colon
            character ::= semicolon
            character ::= single quote
            character ::= double quote
            character ::= equal
            character ::= space
            character ::= tab
            character ::= bang
            character ::= hash
            character ::= dollar
            character ::= percent
            character ::= carrot
            character ::= ampersand
            character ::= star
            character ::= late
            character ::= rate
            character ::= minus
            character ::= underscore
            character ::= plus
            character ::= backslash
            character ::= dot
            character ::= dit
            character ::= slash
            character ::= question
            character ::= comma
        '''
        value = {
            'act'   : 'Escape',
            'colon' : 'colon',
            'semicolon' : 'semicolon',
            'single': 'apostrophe',
            'double': 'quotedbl',
            'equal' : 'equal',
            'space' : 'space',
            'tab'   : 'Tab',
            'bang'  : 'exclam',
            'hash'  : 'numbersign',
            'dollar': 'dollar',
            'percent': 'percent',
            'carrot': 'caret',
            'ampersand': 'ampersand',
            'star': 'asterisk',
            'late': 'parenleft',
            'rate': 'parenright',
            'minus': 'minus',
            'underscore': 'underscore',
            'plus': 'plus',
            'backslash': 'backslash',
            'dot': 'period',
            'dit': 'period',
            'slash': 'slash',
            'question': 'question',
            'comma': 'comma'
        }
        return AST('raw_char', [ value[args[0].type] ])

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

    def p_modifiers(self, args):
        '''
            modifiers ::= control single_command
            modifiers ::= alt single_command
            modifiers ::= alternative single_command
        '''
        value = {
            'control' : 'ctrl',
            'alt' : 'alt',
            'alternative' : 'alt'
        }
        if(args[1].type == 'mod_plus_key'):
            args[1].meta.insert(0, value[args[0].type])
            return args[1]
        else:
            return AST('mod_plus_key', [ value[args[0].type] ], [ args[1] ] )

    @add_rules_for_terminals("english ::= word {}")
    def p_english(self, args):
        '''
            english ::= word ANY
        '''
        if args[1].type != 'ANY':
            return AST('sequence', [ args[1].type ])
        return AST('sequence', [ args[1].extra ])

    def p_word_sentence(self, args):
        '''
            word_sentence ::= sentence word_repeat
        '''
        if(len(args[1].children) > 0):
            args[1].children[0].meta = args[1].children[0].meta.capitalize()
        return args[1]

    def p_word_phrase(self, args):
        '''
            word_phrase ::= phrase word_repeat
        '''
        return args[1]

    def p_word_repeat(self, args):
        '''
            word_repeat ::= raw_word
            word_repeat ::= raw_word word_repeat
        '''
        if(len(args) == 1):
            return AST('word_sequence', None,
                [ AST('null', args[0]) ])
        else:
            args[1].children.insert(0, AST('null', args[0]))
            return args[1]

    # 'exclusions' contains the terminals that should continue to be
    # treated as commands. As it is, the list is somewhat arbitrary;
    # it contains modifier keys and a subset of the special characters from
    # the "p_character" rule. Modify as desired.
    @add_rules_for_terminals("raw_word ::= {}", exclusions = \
                             ['control', 'alt', 'alternative',
                              'colon', 'semicolon', 'bang', 'hash', 'percent',
                              'ampersand', 'star', 'minus', 'underscore', 'plus',
                              'backslash', 'question', 'comma'])
    def p_raw_word(self, args):
        '''
            raw_word ::= ANY
        '''
        if(args[0].type == 'ANY'):
            return args[0].extra
        return args[0].type

    # camelCase rule, from Tomas Kanocz' Silvius fork
    # (https://github.com/KanoczTomas/silvius)
    def p_word_camel(self, args):
        '''
            word_camel ::= word_camel_name word_repeat
        '''
        #print dir(args[1])
        if(len(args[1].children) > 0):
            camelCase = ''
            first = True #we use it not to capitalise the first character
            for a in args[1].children:
                if first:
                    camelCase += a.meta
                    first = False
                else:
                    camelCase += a.meta.capitalize()
                    
            args[1].children[0].meta = camelCase
            child = deepcopy(args[1].children[0])
            del args[1].children #we throw away all childes
            args[1].children = [child] #insert only the 1 generated and having the camelCase meta
        
        return args[1]
    
    def p_word_camel_name(self, args):
        '''
            word_camel_name ::= campbell
            word_camel_name ::= camel
        '''
    
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
            emacs_cmd ::= emacs_name eat
            emacs_cmd ::= emacs_name close
            emacs_cmd ::= emacs_name search
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
        elif args[1].type == 'eat':
            sequence.append(AST('raw_char', [ 'Escape'] ))
            sequence.append(AST("char", [ 'd'] ))
        elif args[1].type == 'close':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 'x'] ) ] ))
            sequence.append(AST('char', [ 'k'] ))
        elif args[1].type == 'search':
            sequence.append(AST('mod_plus_key', [ 'ctrl' ], [ AST("char", [ 's'] ) ] ))
        return AST("chain", None, sequence)

    def p_emacs_name(self, args):
        '''
            emacs_name ::= last
        '''
        return args[0]
    
        
class SingleInputParser(CoreParser):
    def __init__(self):
        # if you have the issue that commands fail because spurious
        # tokens ('i', 'the',...) are prepended to the acual command,
        # try commenting the 'single_input' line, and uncommenting
        # the 'single_input_discard_junk' line.
        CoreParser.__init__(self, 'single_input')
        #CoreParser.__init__(self, 'single_input_discard_junk')
        self.sleeping = False

    def p_sleep_commands(self, args):
        '''
            sleep_commands ::= go to sleep
            sleep_commands ::= start listening
        '''
        if args[-1].type == 'sleep':
            self.sleeping = True
            print 'Going to sleep.'
        else:
            self.sleeping = False
            print 'Waking from sleep'
        return AST('')

    def p_single_input(self, args):
        '''
            single_input ::= END
            single_input ::= sleep_commands END
            single_input ::= chained_commands END
        '''
        if len(args) > 0 and not self.sleeping:
            return args[0]
        else:
            return AST('')

    def p_single_input_discard_junk(self, args):
        '''
            single_input_discard_junk ::= END
            single_input_discard_junk ::= junk_tokens sleep_commands END
            single_input_discard_junk ::= junk_tokens chained_commands END
        '''
        if len(args) > 1 and not self.sleeping:
            return args[1]
        else:
            return AST('')

    # With some models, Kaldi may return spurious tokens in response
    # to noise. If that happens just before we say a command, it will
    # make the command fail. This "dummy" rule will swallows these tokens.
    def p_junk_tokens(self, args):
        '''
            junk_tokens ::=
            junk_tokens ::= i junk_tokens
            junk_tokens ::= the junk_tokens
            junk_tokens ::= a junk_tokens
            junk_tokens ::= and junk_tokens
        '''
        return AST('')


def parse(parser, tokens):
    return parser.parse(tokens)
