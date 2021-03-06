import sys

from lark import Lark, Transformer, v_args

import lpp_parser


class LppEvaluator():
    def __init__(self):
        self.lpp_parser = lpp_parser.get_lpp_parser()

    def evaluate(self, program: str):
        tree = self.lpp_parser.parse(program)
        # the state is a function state : ide -> int
        # the empty state is represented by the 
        # constant function 0, since we dont have to declare variables
        self.evalutate_program(tree, (lambda s : 0))

    # simple state-passing interpreter
    def evalutate_program(self, tree, state):
        if tree.data == "composition":
            # basically compose the statements
            s1, s2 = tree.children
            return self.evalutate_program(s2, 
                    self.evalutate_program(s1, state))

        elif tree.data == "if":
            guard, s1, s2 = tree.children
            # apply the semantics of the if statement
            if (self.evaluate_bool_expr(guard, state)):
                return self.evalutate_program(s1, state)
            else:
                return self.evalutate_program(s2, state)

        elif tree.data == "while":
            guard, c = tree.children
            # apply kind of boringly the semantics of the while statement
            new_state = state
            while(self.evaluate_bool_expr(guard, new_state)):
                new_state = self.evalutate_program(c, new_state)
            return new_state

        elif tree.data == "print":
            # just print the evaluated expression, what did you expect?
            for e in tree.children:
                print(self.evaluate_expr(e, state))
            return state
        
        elif tree.data == "skip":
            # do nothing, successfully
            return state

        elif tree.data == "assignment":
            ide, exp = tree.children
            value = self.evaluate_expr(exp, state)
            # this is where things start to get exciting
            # because there is the notion of change in state!
            # this is really cool, it is kind of a nested lambda
            # this new function is equivalent to the 
            # substitution state[value/ide]
            return (lambda s: value if (s == ide) else state(s))


    # simply evaluate a boolean expression
    def evaluate_bool_expr(self, tree, state) -> bool:
        if tree.data == "le":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) <= self.evaluate_expr(e2, state)
        elif tree.data == "ge":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) >= self.evaluate_expr(e2, state)
        elif tree.data == "eq":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) == self.evaluate_expr(e2, state)
        elif tree.data == "neq":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) != self.evaluate_expr(e2, state)
        elif tree.data == "lt":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) < self.evaluate_expr(e2, state)
        elif tree.data == "gt":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) > self.evaluate_expr(e2, state)
        elif tree.data == "and":
            e1, e2 = tree.children
            return self.evaluate_bool_expr(e1, state) and self.evaluate_bool_expr(e2, state)
        elif tree.data == "or":
            e1, e2 = tree.children
            return self.evaluate_bool_expr(e1, state) or self.evaluate_bool_expr(e2, state)
        elif tree.data == "not":
            e1 = tree.children[0]
            return not self.evaluate_bool_expr(e1, state)

    # simply evaluate an integer expression
    def evaluate_expr(self, tree, state) -> int:
        if tree.data == "add":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) + self.evaluate_expr(e2, state)
        elif tree.data == "sub":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) - self.evaluate_expr(e2, state)
        elif tree.data == "mul":
            e1, e2 = tree.children
            return self.evaluate_expr(e1, state) * self.evaluate_expr(e2, state)
        elif tree.data == "div":
            e1, e2 = tree.children
            # NOTE support only for integer division
            return self.evaluate_expr(e1, state) // self.evaluate_expr(e2, state)
        elif tree.data == "number":
            return int(tree.children[0])
        elif tree.data == "var":
            return state(tree.children[0])

def run_repl():
    # run an interactive shell
    evaluator = LppEvaluator()
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        evaluator.evaluate(s)

def main():
    # if a filename is provided via command line
    # execute it, else run the repl
    if(len(sys.argv) >= 2):
        with open(sys.argv[1]) as f:
            evaluator = LppEvaluator()
            evaluator.evaluate(f.read())
    else:
        run_repl()

if __name__ == '__main__':
    main()
