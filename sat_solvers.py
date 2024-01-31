class Expression:
    
    operator_signs = {
        'neg' : '~',
        'and' : ' & ',
        'or' : ' | ',
        'implies' : '->'
    }
    
    replacements = {
        '(' : ' ( ',
        ')' : ' ) ',
        '[' : ' ( ',
        ']' : ' ) ',
        '{' : ' ( ',
        '}' : ' ) ',
        '~' : ' ~ ',
        '&' : ' & ',
        '|' : ' | ',
        '->' : ' -> '
    }
    
    reserved = ['(', ')', '~', '&', '|', '->', 'T', 'F']
    
    def __init__(self, expr : str):
        # Defining object properties
        self.expression = ''
        self.sub_terms = {}
        
        # If expression is empty, then break
        if not expr.strip():
            return
        
        expr = '(' + expr + ')'
        # Applying spacing
        for key, value in Expression.replacements.items():
            expr = expr.replace(key, value)
        tokens = expr.split()
        
        # Removing whitespace from tokens
        tokens = [token.strip() for token in tokens]
        
        for i, token in enumerate(tokens):
            # if expr[i] is 'and', 'or', 'implies', then replace them with their sign
            if token.lower() in Expression.operator_signs.keys():
                tokens[i] = Expression.operator_signs[token.lower()]
            # if expr[i] is not reserved, then it is a variable 
            elif token not in Expression.reserved:
                tokens[i] = VAR.get_unique(token, self)
        
        self.expression = self.parse_expression(tokens)
    
    def parse_expression(self, expr):
        stacks = []
        for token in expr:
            if token == '(':
                stacks.append([])
            elif token == ')':
                expression = self.build_expression(stacks.pop())
                if not stacks:
                    return expression
                stacks[-1].append(expression)
            else:
                stacks[-1].append(token)
        
        # At this point, the stack should only contain a single expression
        return stacks[0]

    def build_expression(self, tokens):
        if len(tokens) == 1:
            return tokens[0]
                
        # Applying negs
        new_tokens = []
        i = len(tokens) - 1
        while i >= 0:
            if tokens[i] == '~':
                new_tokens.append(NEG.get_unique(new_tokens.pop(), self))
            else:
                new_tokens.append(tokens[i])
            i -= 1
        new_tokens = new_tokens[::-1]
        
        # Applying operators
        expression = new_tokens[0]
        for i, token in enumerate(new_tokens):
            if token == '|':
                expression = OR.get_unique(expression, new_tokens[i+1], self)
            elif token == '&':
                expression = AND.get_unique(expression, new_tokens[i+1], self)
            elif token == '->':
                expression = IMPLY.get_unique(expression, new_tokens[i+1], self)
            
        return expression
    
    def estimate(self, assignment : dict):
        return self.expression.estimate(assignment)
    
    def update_sub_terms(self):
        hash = str(self)
        if hash in self.expression.sub_terms.keys():
            return self.expression.sub_terms[hash]
        else:
            self.expression.sub_terms[hash] = self
            return self
        
    def linear_sat_solver(self, reset_values=True):
        self.expression.set_value(True)
        self.expression.top_down()
        
        for node in self.sub_terms.values():
            node.bottom_up()
        
        result = None
        if self.found_contradiction():
            result = (-1, 'Contradiction found! There is no answer for the given expression...')
        elif self.all_nodes_assigned():
            result = (1, {var.sign:var.temp_val for var in self.sub_terms.values() if isinstance(var, VAR)})
        else:
            result = (0, 'Failure! Could not decide on the expressions constraints...')
        
        if reset_values:
            self.expression.reset_values()
        return result
    
    def cubic_sat_solver(self, reset_values=True):
        signal, message = self.linear_sat_solver(reset_values=False)
        
        if signal == 1 or signal == -1:
            return signal, message
        
        found_contradiction = False
        terms_list = list(self.sub_terms.values())
        for hash, term in self.sub_terms.items():
            if term.temp_val != None:
                continue
            
            contradictions = []
            vals = []
            expressions = []
            for value in [True, False]:
                new_expr = self.copy()
                new_expr.sub_terms[hash].set_value(value)
                new_expr.sub_terms[hash].top_down()
                for node in new_expr.sub_terms.values():
                    node.bottom_up()
                contradictions.append(new_expr.found_contradiction())
                vals.append([term.temp_val for term in new_expr.sub_terms.values()])
                expressions.append(new_expr)
            
            # If both values of subterm ends in contradiction, then there is no answer...
            if contradictions[0] == contradictions[1] == True:
                found_contradiction = True
                break
            
            elif contradictions[0] == False and expressions[0].all_nodes_assigned():
                if reset_values:
                    self.expression.reset_values()
                return (1, {hash:term.temp_val for  hash, term in expressions[0].sub_terms.items() if isinstance(term, VAR)})
                
            elif contradictions[1] == False and expressions[1].all_nodes_assigned():
                if reset_values:
                    self.expression.reset_values()
                return (1, {hash:term.temp_val for  hash, term in expressions[1].sub_terms.items() if isinstance(term, VAR)})
                
            elif contradictions[0] == contradictions[1] == False:
                for i in range(len(vals[0])):
                    if (vals[0][i] != None) and (vals[0][i] == vals[1][i]):
                        terms_list[i].set_value(vals[0][i])
                
            elif contradictions[0] == False:
                term.set_value(True)
                
            elif contradictions[1] == False:
                term.set_value(False)
            
        if found_contradiction or self.found_contradiction():
            result = (-1, 'Contradiction found! There is no answer for the given expression...')
        elif self.all_nodes_assigned():
            result = (1, {var.sign:var.temp_val for var in self.sub_terms.values() if isinstance(var, VAR)})
        else:
            result = (0, 'Failure! Could not decide on the expressions constraints...')
            
        if reset_values:
            self.expression.reset_values()
        return result
        
    def horn(self):
        new_expr = Expression('')
        new_expr.expression = self.expression.horn(new_expr)
        return new_expr
        
    def copy(self):
        new_expr = Expression('')
        new_expr.expression = self.expression.copy(new_expr)
        return new_expr
    
    def found_contradiction(self):
        return any([node.found_contradiction == True for node in self.sub_terms.values()])
    
    def all_nodes_assigned(self):
        return all([node.temp_val != None for node in self.sub_terms.values()])
    
    def set_value(self, value):
        if (self.temp_val != None) and ((not self.temp_val) == value):
            self.found_contradiction == True
        self.temp_val = value

    def __repr__(self):
        return str(self.expression)

class VAR(Expression):
    
    def __init__(self): pass        
    
    @staticmethod
    def get_unique(sign, expression, temp_val = None):
        if isinstance(sign, Expression):
            return sign
        self = VAR()
        self.sign = sign
        self.expression = expression
        self.temp_val = temp_val # Boolean value
        self.found_contradiction = False # Boolean value
        
        return self.update_sub_terms()

    def estimate(self, assignment: dict):
        if self.sign == 'T':
            return True
        if self.sign == 'F':
            return False
        return assignment[self.sign]
    
    def top_down(self):
        pass # Nothing to do on a variable
    
    bottom_up = top_down
    
    def horn(self, expression):
        return VAR.get_unique(self.sign, expression)
    
    def copy(self, expression):
        return VAR.get_unique(self.sign, expression, temp_val=self.temp_val)

    def reset_values(self):
        self.temp_val = None
        self.found_contradiction = False

    def __repr__(self):
        return self.sign

class AND(Expression):
    
    def __init__(self): pass
    
    @staticmethod
    def get_unique(left, right, expression, temp_val = None):
        self = AND()
        if str(left) > str(right):
            left, right = right, left
        self.left = left
        self.right = right
        self.expression = expression
        self.temp_val = temp_val # Boolean value
        self.found_contradiction = False # Boolean value
        
        return self.update_sub_terms()
        
    def estimate(self, assingment : dict):
        return self.left.estimate(assingment) and self.right.estimate(assingment)
    
    def top_down(self):
        if self.temp_val == True:
            self.left.set_value(True)
            self.right.set_value(True)
        
        self.left.top_down()
        self.right.top_down()
        
    def bottom_up(self):
        if self.left.temp_val == self.right.temp_val == True:
            self.set_value(True)
            
        elif self.left.temp_val == False or self.right.temp_val == False:
            self.set_value(False)
            
        elif self.temp_val == False and self.left.temp_val == True:
            self.right.set_value(False)
            
        elif self.temp_val == False and self.right.temp_val == True:
            self.left.set_value(False)
    
    def horn(self, expression):
        return AND.get_unique(self.left.horn(expression), self.right.horn(expression), expression)
    
    def copy(self, expression):
        return AND.get_unique(self.left.copy(expression), self.right.copy(expression), expression, temp_val=self.temp_val)
        
    def reset_values(self):
        self.temp_val = None
        self.found_contradiction = False
        self.left.reset_values()
        self.right.reset_values()
    
    def __repr__(self):
        return f'({str(self.left)} & {str(self.right)})'
    
class OR(Expression):
    
    def __init__(self): pass
    
    @staticmethod
    def get_unique(left, right, expression, temp_val = None):
        self = OR()
        if str(left) > str(right):
            left, right = right, left
        self.left = left
        self.right = right
        self.expression = expression
        self.temp_val = temp_val # Boolean value
        self.found_contradiction = None # Boolean value
        
        return self.update_sub_terms()
        
    def estimate(self, assingment : dict):
        return self.left.estimate(assingment) or self.right.estimate(assingment)
    
    def top_down(self):
        raise RuntimeError('Linear SAT solver must only be used on a horn caluse!')
    
    bottom_up = top_down
    
    def horn(self, expression):
        return NEG.get_unique(AND.get_unique(self.left.horn(expression), self.right.horn(expression), expression), expression)
    
    def copy(self, expression):
        return OR.get_unique(self.left.copy(expression), self.right.copy(expression), expression, temp_val=self.temp_val)
    
    reset_values = AND.reset_values
    
    def __repr__(self):
        return f'({str(self.left)} | {str(self.right)})'
    
class IMPLY(Expression):
    
    def __init__(self): pass
    
    def get_unique(left, right, expression, temp_val = None):
        self = IMPLY()
        self.left = left
        self.right = right
        self.expression = expression
        self.temp_val = temp_val # Boolean value
        self.found_contradiction = None # Boolean value

        return self.update_sub_terms()
        
    def estimate(self, assignment : dict):
        return (not self.left.estimate(assignment)) or self.right.estimate(assignment)
    
    def top_down(self):
        raise RuntimeError('Linear SAT solver must only be used on a horn caluse!')
    
    bottom_up = top_down
    
    def horn(self, expression):
        return NEG.get_unique(
            AND.get_unique(self.left.horn(expression), NEG.get_unique(self.right.horn(expression), expression), expression),
            expression)
    
    def copy(self, expression):
        return IMPLY.get_unique(self.left.copy(expression), self.right.copy(expression), expression, temp_val=self.temp_val)
        
    reset_values = AND.reset_values
        
    def __repr__(self):
        return f'({str(self.left)} -> {str(self.right)})'
    
class NEG(Expression):
    
    def __init__(self): pass
    
    def get_unique(atom, expression, temp_val = None):
        self = NEG()
        self.atom = atom
        self.expression = expression
        self.temp_val = temp_val # Boolean value
        self.found_contradiction = None # Boolean value
        
        return self.update_sub_terms()
    
    def estimate(self, assingment : dict):
        return not self.atom.estimate(assingment)
    
    def top_down(self):
        if self.temp_val != None:
            self.atom.set_value(not self.temp_val)
        self.atom.top_down()
        
    def bottom_up(self):
        if self.atom.temp_val != None:
            self.set_value(not self.atom.temp_val)
    
    def horn(self, expression):
        return NEG.get_unique(self.atom.horn(expression), expression)
    
    def copy(self, expression):
        return NEG.get_unique(self.atom.copy(expression), expression, temp_val=self.temp_val)
    
    def reset_values(self):
        self.temp_val = None
        self.found_contradiction = False
        self.atom.reset_values()
    
    def __repr__(self):
        return f'~{str(self.atom)}'
