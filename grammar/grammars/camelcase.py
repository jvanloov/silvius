from copy import deepcopy

# This subgrammar requires the EnglishGrammarMixin, for
# the "word_repeat" rule

class CamelCaseMixin(object):

    def __init__(self, *args, **kwargs):
        # register this subgrammar on the main grammar in CoreParser
        self.add_subgrammar(["word_camel"])

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
