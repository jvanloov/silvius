# Parser, based on John Aycock's SPARK examples

from sys import exit
from spark import GenericParser
from spark import GenericASTBuilder
from ast import AST

# subgrammars are loaded from the grammars/ subpackage
from grammars import numbers
from grammars import english
from grammars import yesno
from grammars import camelcase
from grammars import shell
from grammars import emacs

class GrammaticalError(Exception):
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string

# include the subgrammars as mixin classes. This makes all the rule
# functions accessible in the CoreParser (and the actual parser in
# GenericParser), and allows the subgrammar classes to call
# 'add_subgrammar' from their __init__ methods.
class CoreParser(GenericParser,
                 numbers.NumberGrammarMixin,
                 english.EnglishGrammarMixin,
                 yesno.YesNoGrammarMixin,
                 camelcase.CamelCaseMixin,
                 shell.ShellCmdMixin,
                 emacs.EmacsMixin):

    terminals = []

    def __init__(self, start):
        # call __init__ on all mixin classes
        # skip GenericParser, we'll call that as the last one
        for base in CoreParser.__bases__:
            if base.__name__ is not "GenericParser":
                base.__init__(self, start)
        # now set up the actual parser
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
    # The function below, and the function decorator in parse_utils.py, work
    # together to automate this.
    # (The decorator is needed to modify the docstring programmatically.)

    def install_terminal_rules(self):
        # if we have a list of terminals available: collect all rules from this
        # class and the base classes (= subgrammars). Loop over the rule
        # functions; if they were annotated with @add_rules_for_terminals,
        # we add new rules based on the template for that rule and the terminals.
        if len(self.terminals) > 0:
            # collect all classes, and filter out rule functions (p_...)
            # from their function dictionaries
            base_classes = [base
                            for base in CoreParser.__bases__
                            if base.__name__ is not "GenericParser"]
            base_classes += [CoreParser]
            rule_data = []
            for base_class in base_classes:
                rule_data += [(rule_name, base_class)
                              for rule_name in base_class.__dict__
                              if "p_" in rule_name]
            # detect duplicate rule names:
            rule_names = [rule[0] for rule in rule_data]
            duplicates = set([rule_name for rule_name in rule_names
                              if rule_names.count(rule_name) > 1])
            if len(duplicates) > 0:
                print "You have duplicate rule names:", ", ".join(duplicates)
                exit()
            # Loop over all rules, and add the new rules from the
            # terminal list if desired.
            for (rule_name, base_class) in rule_data:
                function = base_class.__dict__[rule_name]
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


    # this method will be called by any subgrammars that want
    # to hook themselves into the main grammar.
    # this adds one or more rules to the 'single_command' ruleset.
    def add_subgrammar(self, subgrammar_start_rule_names):
        func = CoreParser.__dict__['p_single_command']
        for start_rule_name in subgrammar_start_rule_names:
            func.__doc__ += ("single_command ::= " + start_rule_name + "\n")


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
            single_command ::= movement
            single_command ::= character
            single_command ::= editing
            single_command ::= modifiers
        '''
        return args[0]

    def p_movement(self, args):
        '''
            movement ::= up     repeat
            movement ::= down   repeat
            movement ::= left   repeat
            movement ::= right  repeat
        '''
        if args[1] != None:
            return AST('repeat', [ args[1] ], [
                AST('movement', [ args[0] ])
            ])
        else:
            return AST('movement', [ args[0] ])

    def p_repeat(self, args):
        '''
            repeat ::=
            repeat ::= number_set
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None


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
            letter ::= golf
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
