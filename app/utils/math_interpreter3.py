#Interpreter: math-interpreter

# Simple Math Interpreter
from decimal import Decimal
# Tokens Type: Syntax
LPARENT, RPARENT, EOF = 'LPARENT', 'RPARENT', 'EOF'
# Tokens Type: Operaciones
PLUS, MINUS, MULT, POW, DIV, MOD = 'PLUS', 'MINUS', 'MULT', 'POW', 'DIV', 'MOD'
# Tokens Type: Data and Values:
INTEGER, REAL, PERCENT, ID, COMMA = 'INTEGER', 'REAL', 'PERCENT', 'ID', 'COMMA'

class Percent():
    def __init__(self, value):
        self._value = value

    def __add__(self, other):
        if isinstance(other, Percent):
            return Percent(other.value100 + self.value100)

        return other * (1 + self.value)

    def __sub__(self, other):
        if isinstance(other, Percent):
            return Percent(self.value100 - other.value100)

        return other * (1 - self.value)

    def __mul__(self, other):
        if isinstance(other, Percent):
            return Percent(other.value100 * self.value)

        return other * (self.value)

    def __div__(self, other):
        if isinstance(other, Percent):
            return Percent(self.value100 / other.value)

        return other / (self.value)

    def __truediv__(self, other):
        if isinstance(other, Percent):
            return Percent(other.value100 // self.value)

        return other // (self.value)

    def __mod__(self, other):
        if isinstance(other, Percent):
            return Percent(other.value100 % self.value)

        return other % (self.value)

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        print("r")
        return self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rdiv__(self, other):
        return self.__div__(other)
    
    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __rmod__(self, other):
        return self.__mod__(other)

    def __not__(self):
        return Percent(-self.value100)

    def get_value(self):
        return self._value/100

    def get_value100(self):
        return self._value

    value = property(get_value)
    value100 = property(get_value100)

    def __int__(self):
        return int(self.value100)

    def __float__(self):
        return float(self.value100)

    def __str__(self):
        return f"{self.value100}%"

    def __repr__(self):
        return f"Percent({self.value100!r})"

class Token():
    def __init__(self, _type, value):
        self.type = _type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value!r})"

    def __repr__(self):
        return self.__str__()

class Lexer():
    def __init__(self):
        self.restart() #Start and Restart
        self.var_characters = "abcdefghijklmnopqrstuvwxyzñ_"+"abcdefghijklmnopqrstuvwxyzÑ".upper()
        self.use_decimal_class = True

    def restart(self, text=None):
        self.text = text
        self.pos = 0
        if self.text == None:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def error(self):
        print("Lexer error: Invalid syntax.")

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespaces()
                continue

            if self.current_char.isdigit() or self.current_char in ".%":
                return self.integer_or_float()

            if self.current_char in self.var_characters:
                return Token(ID, self.variable())
            
            if self.current_char == "+":
                token = Token(PLUS, "+")
                self.advance()
                return token

            if self.current_char == "-":
                token = Token(MINUS, "-")
                self.advance()
                return token

            if self.current_char == "*" and self.peek(1) == "*":
                token = Token(POW, "**")
                self.advance(2)
                return token

            if self.current_char == "*":
                token = Token(MULT, "*")
                self.advance()
                return token

            if self.current_char == "/":
                token = Token(DIV, "/")
                self.advance()
                return token
                
            if self.current_char == "~":
                token = Token(MOD, "~")
                self.advance()
                return token 


            if self.current_char == "(":
                token = Token(LPARENT, "(")
                self.advance()
                return token

            if self.current_char == ")":
                token = Token(RPARENT, ")")
                self.advance()
                return token

            if self.current_char == ",":
                token = Token(COMMA, ",")
                self.advance()
                return token

            self.error()
            break

        return Token(EOF, None)

    def skip_whitespaces(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer_or_float(self):
        result = ""
        while self.current_char is not None and self.current_char in "0123456789.e%":
            if self.current_char == ".":
                if '.' in result:
                    break
            elif self.current_char == "e":
                if not '.' in result:
                    result += ".0"
            
            elif self.current_char == "%":
                if not '%' in result:
                    result = "%"+result
                    self.advance()
                    break
                elif result=="":
                    pass
                else:
                    break

            result += self.current_char
            self.advance()

        if "." in result:
            if result.endswith("."):
                result += "0"
            if result.startswith("."):
                result = "0"+result

            if result.startswith("%"):
                return Token(PERCENT, Percent(float(result[1:])))

            elif self.use_decimal_class:
                return Token(REAL, Decimal(result))
            else:
                return Token(REAL, float(result))
        else:
            if result.startswith("%"):
                return Token(PERCENT, Percent(int(result[1:])))
            else:
                return Token(INTEGER, int(result))

    def variable(self):
        result = ""
        while self.current_char is not None and self.current_char in self.var_characters:
            result += self.current_char
            self.advance()

        return str(result)

    def advance(self, value=1):
        self.pos += value
        if self.pos >= len(self.text):
            self.current_char = None 
        else:
            self.current_char = self.text[self.pos]

    def peek(self, value):
        v = self.pos + value
        if v >= len(self.text):
            return None
        else:
            return self.text[v]

class Interpreter():
    def __init__(self, lexer, variables, funciones):
        self.lexer = lexer
        self.current_token = None
        self.global_variables = variables 
        self.global_funciones = funciones

    def error(self):
        print("Interpreter Error: Invalid syntax")
    
    def eat(self, token_type):
        #print("EAT", self.current_token, "AS", token_type)
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()

        else:
            self.error()

    def func(self):
        """ func: ID LPARENT expr (COMMA expr)*  RPARENT """
        token = self.current_token
        func_id = token.value
        self.eat(ID)

        result = None
        args = []
        if self.current_token.type == LPARENT:
            self.eat(LPARENT)
            if self.current_token.type != RPARENT:
                args.append( self.expr() )
                while (self.current_token.type in (COMMA,)):
                    self.eat(COMMA)
                    args.append(self.expr())

            self.eat(RPARENT)
            func_object = self.global_funciones.get(func_id, None)
            if func_object is not None:
                result = func_object(*args)

        if result is None:
            self.error()
            
        return result

    def factor(self):
        """ factor: (PLUS|MINUS)?(INTEGER|REAL|PERCENT|ID|func|(LPARENT expr RPARENT)) """
        
        token = self.current_token
        
        if token.type in (PLUS, MINUS):
            if token.type == MINUS:
                self.eat(MINUS)
                return -self.factor()

            elif token.type == PLUS:
                self.eat(PLUS)
                return self.factor()
            
        if token.type == INTEGER:
            self.eat(INTEGER)
            result = token.value

        elif token.type == REAL:
            self.eat(REAL)
            result = token.value

        elif token.type == PERCENT:
            self.eat(PERCENT)
            result = token.value

        elif token.type == ID:
            result = self.global_variables.get(token.value, None)
            if result == None:
                result = self.func()
            else:
                self.eat(ID)
        
        elif token.type == LPARENT:
            self.eat(LPARENT)
            result = self.expr()
            self.eat(RPARENT)

        return result

    def term_pow(self):
        """ term_pow: factor (POW factor)*
            term_pow: factor factor"""

        result = self.factor()

        while self.current_token.type in (POW, INTEGER, REAL, ID, LPARENT):
            op = self.current_token

            if op.type == POW:
                self.eat(POW)
                result = result ** self.factor()

            #INTEGER, REAL, ID, LPARENT
            else:
                result = result * self.factor()

        return result 

    def term(self):
        """ term: term_pow ((MULT|DIV|MOD) factor)* """

        result = self.term_pow()

        while self.current_token.type in (MULT, DIV, MOD):
            op = self.current_token

            if op.type == MULT:
                self.eat(MULT)
                result = result * self.term_pow()
            
            elif op.type == DIV:
                self.eat(DIV)
                result = result / self.term_pow()

            elif op.type == MOD:
                self.eat(MOD)
                result = result % self.term_pow()

        return result 

    def expr(self):
        """ expr: term ((PLUS|MINUS) term) """

        result = self.term()

        while self.current_token.type in (PLUS, MINUS):
            op = self.current_token

            if op.type == PLUS:
                self.eat(PLUS)
                result = result + self.term()
            
            elif op.type == MINUS:
                self.eat(MINUS)
                result = result - self.term()


        return result 
            
    def parse(self, text = None):
        if text is not None:
            self.lexer.restart(text)
        
        self.current_token = self.lexer.get_next_token()
        return self.expr()

def main():
    lexer = Lexer()
    inter = Interpreter(lexer,
                {'x': 100, 'y': 250, 'z': 1000},
                {'n': lambda x: x*2, 'suma': lambda x, y: x+y})
    while True:
        try:
            code = input("SMI3 > ")

        except BaseException:
            continue

        if not code:
            continue

        elif code == "exit":
            break

        result = inter.parse(code)
        print(result)

if __name__ == '__main__':
    main()
        
