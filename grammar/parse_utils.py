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


