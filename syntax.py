import copy

OK = "Correct" # for correct operation result
ERROR_RES = "ERROR_RESULT" # for invalid operation result
FIN = "End-of-Tokens"

LITERALS = [
    'TROOF_Literal',                 
    'String_Literal',
    'NUMBAR_Literal',
    'NUMBR_Literal',
    'Void_Literal',
]

ARITHMETIC_OPS = {
    "SUM_OF_Arithmetic_Operation": lambda a, b: a + b,
    "DIFF_OF_Arithmetic_Operation": lambda a, b: a - b,
    "PRODUKT_OF_Arithmetic_Operation": lambda a, b: a * b,
    "QUOSHUNT_OF_Arithmetic_Operation": lambda a, b: a // b if b != 0 else None, 
    "MOD_OF_Arithmetic_Operation": lambda a, b: a % b if b != 0 else None,
    "BIGGR_OF_Arithmetic_Operation": lambda a, b: max(a, b),
    "SMALLR_OF_Arithmetic_Operation": lambda a, b: min(a, b)
}

COMPARISON_OPS = {
    "BOTH_SAEM_Comparison_Operation": lambda a, b: a == b,
    "DIFFRINT_Comparison_Operation": lambda a, b: a != b,
}

LOGIC_OPS = {
    "BOTH_OF_Boolean_Operation": lambda a, b: a == "WIN" and b == "WIN",
    "EITHER_OF_Boolean_Operation": lambda a, b: a == "WIN" or b == "WIN",
    "WON_OF_Boolean_Operation": lambda a, b: a != b,
}

INF_LOGIC_OPS = {
    "ANY_OF_BooleanOperation": lambda a: all(a),
    "ALL_OF_Boolean_Operation": lambda a: any(a)
}

"""
NOTES:
All Error tuples must be passed 
"""

class Interpreter:
    def __init__(self, tokens, console=None, gui=None):
        self.tokens = tokens
        self.console = console if console else []
        self.gui = gui

        # self.symbol_table = {"IT": None}  # init IT variable
        self.symbol_table = { "IT": {"value": 'NOOB', "type": "Void_Literal"} } # init IT as NOOB symbol table now has type
        self.functions = {} # todo: separate functions from the symbol table

        self.current_token = None
        self.token_index = -1 # since starting is 0 init to -1
        self.current_line = [] #store tokens in a line to be outputted in console
        self.line_number = 1  # track line number

        # function call tracking
        self.functions_stack = []  # MAYBE Store state of token and symbol table
        self.if_then_stack = [] # store IF-THEN states

        #flags etc.
        self.orly_flag = False
        self.ya_flag = False
        self.wtf_flag = False
        self.omg_flag = False
        self.wazzup_flag = False
        self.wazzup_line = None # track line number to ensure function declarations are after wazzup
        self.inside_function = False
        self.no_function_declarations = False # track if function declarations are declared before statements
        self.inf_logic_statement = False # track if we are evaluation ALL OF and ANY OF
        
        

    """ 
        Move to next token
    """
    def advance(self):
        
        if self.token_index < len(self.tokens)-1:
            print(f"advancing one token....from (l:{self.line_number} n: {self.token_index} ):{self.current_token}")
            # if to-be "previous" token is a LINEBREAK add line_number
            if self.current_token and (self.current_token[1] == "LINEBREAK" or self.current_token[1] == "MULTILINE_COMMENT"):
                self.line_number += 1
                self.current_line = [] #empty current_line
            self.token_index += 1
            self.current_token = self.tokens[self.token_index]
            self.current_line.append(self.current_token)
            print(f"advanced to .... (l:{self.line_number} n: {self.token_index} ):{self.current_token}")
        else:
            self.current_token = None
    
    """ 
        Consume all valid comments and linebreak 
    """
    def skipLine(self):
        print(f"skipping lines (l:{self.line_number} n: {self.token_index} ):{self.current_token}")
        while self.current_token and (self.current_token[1] == "LINEBREAK" or self.current_token[1] == "MULTILINE_COMMENT"):
            print(f"hey skipper (line #{self.line_number}): {self.current_token}")
            self.advance()

    """
        Accepts Error-message string
        Returns Error tuple (error_message, symbol_table)
    """
    def error(self, message):
        return f"(Error on line {self.line_number}): {message}.\nCurrent Token: '{self.current_token[0]}'", self.symbol_table

    """
        Ensure the next token is a linebreak.
    """
    def expect_linebreak(self):
        if not self.current_token or self.current_token[1] != "LINEBREAK":
            return self.error("Expected linebreak after this statement")
        # self.advance()
        return None  # return no error
    
    """
        Ensure the next token is whatever you want to pass
    """
    def expect_tokenType(self, token_type):
        if not self.current_token or self.current_token[1] != token_type:
            return self.error(f"Expected '{token_type}' after this statement")
        return None  # return no error
    
    """
        Checks is token is linebreak
        Returns Bool
    """
    def is_linebreak(self, token):
        return True if token[1] == "LINEBREAK" else False
    
    """
        For viewing next token
    """
    def get_next_token(self):
        if self.token_index < len(self.tokens):
            return self.tokens[self.token_index+1] 
        else:
            return None
        

    """
     Start here for parsing.
    """
    def parse(self):
        self.advance()  # get the first token
        self.skipLine() # skip any comments or linebreaks

        """ FIND HAI delimeter"""
        if not self.current_token or self.current_token[1] != "HAI_Code_Delimiter":
            return self.error("Program must start with 'HAI'")
        self.advance()  # skip HAI
        # ensure HAI has a linebreak
        error = self.expect_linebreak()
        if error:
            return error
        self.advance()
        """ FIND WAZZUP block"""
        while self.current_token and self.current_token[1] != "HOW_IZ_I_Function_Keyword" and self.current_token[1] != "KTHXBYE_Code_Delimiter":
            self.skipLine() # skip any comments or linebreaks
            
            if self.current_token[1] == "WAZZUP_Variable_Declaration_Delimiter":
                self.wazzup_flag = True
                self.advance()  # skip WAZZUP
                error = self.expect_linebreak() # ensure WAZZUP has a linebreak
                if error:
                    return error
                self.advance()
                # parse only variable declarations in the WAZZUP block
                self.skipLine()
                while self.current_token and self.current_token[1] != "BUHBYE_Variable_Declaration_Delimiter":
                    if self.current_token[1] == "I_HAS_A_Variable_Declaration":
                        error = self.perform_assign()
                        if error:
                            return error
                        self.skipLine()     
                    else:
                        return self.error("Only 'I HAS A' declarations are allowed inside 'WAZZUP' block")

                # parse BUHBYE delimeter
                if not self.current_token or self.current_token[1] != "BUHBYE_Variable_Declaration_Delimiter":
                    return self.error("Expected 'BUHBYE' to end 'WAZZUP' block")
                self.wazzup_line = self.line_number
                self.advance()  # Skip BUHBYE
                error = self.expect_linebreak() # ensure BUHBYE has a linebreak
                if error:
                    return error
                self.wazzup_flag = False # update not in wazzup_block
                break
            elif self.current_token[1] == "I_HAS_A_Variable_Declaration":
                return self.error("Only 'I HAS A' declarations are allowed inside 'WAZZUP' block")
            else:
                break

        
        print(f'The current token: {self.current_token} @line({self.line_number})')
        # if self.current_token[1] == "HOW_IZ_I_Function_Keyword":
        #     self.advance()
        #     while self.current_token and self.current_token[1] != "HOW_IZ_I_Function_Keyword":
        #         self.skipLine()
        #         if self.current_line == "HOW_IZ_I_Function_Keyword":
        #             error = self.perform_function_definition()
        #             if error:
        #                 return error
        #             self.skipLine()
        #         elif self.current_token[1] == "WAZZUP_Variable_Declaration_Delimiter":
        #             return self.error("Expected 'WAZZUP' block to be delcared before Function declarations")
        #         else:
        #             break

        
        """ PARSE OTHER STATMENTS PER LINE"""
        self.skipLine() #skip comments or linebreak tokens
        while self.current_token and self.current_token[1] != "KTHXBYE_Code_Delimiter":
            """todo PASRE function declarations """
            if self.current_token[1] == "HOW_IZ_I_Function_Keyword":
                if self.no_function_declarations == True:
                    return self.error("Functions are to be declared before other statements")
                error = self.perform_function_definition()
                if error:
                    return error
            elif self.current_token[1] == "WAZZUP_Variable_Declaration_Delimiter":
                return self.error("Expected 'WAZZUP' block to be delcared before Function declarations")
            else: 
                self.no_function_declarations = True
                # parse a valid statement per line
                error = self.statement()
                if error:
                    return error
                # ensure there is a line break after every statement
                # error = self.expect_linebreak()
                # if error:
                #     return error
            self.skipLine() #skip comments or linebreak tokens

        if not self.current_token or self.current_token[1] != "KTHXBYE_Code_Delimiter":
            return self.error("Program must end with 'KTHXBYE' Delimiter")
        self.advance()  
        error = self.expect_linebreak() # ensure KTHXBYE has a linebreak
        if error:
            return error
        self.skipLine()
        self.advance()   
        if self.current_token:
            return self.error("No code after 'KTHXBYE'. Only comments allowed.")

        return OK, self.symbol_table
        #end of def parse()


    """
        General Statement patterns per line
        Handles the (tuple, CODE)
        Returns error-tuple if (tuple, ERROR_RES) or None if no error

        For valid statements: the self.current_token must be a linebreak before returning to parse()
    """
    def statement(self):
        token_type = self.current_token[1]

        if token_type == "VISIBLE_Output_Keyword":
            return self.perform_visible()
        elif token_type == "I_HAS_A_Variable_Declaration":
            return self.error("Variable must be declared in 'WAZZUP-BUHBYE' block")
        elif self.wazzup_flag and self.current_token[1] == "WAZZUP_Variable_Declaration_Delimiter":
            return self.error("Only one 'WAZZUP' block is allowed")
        elif token_type == "GIMMEH_Input_Keyword":
            return self.perform_gimmeh()
        
        #todo ADD MORE expressions to be in perform_it_assign
        # in original lolcode as long as something has a return value it will be assigned to IT variable 
        # add smoosh, comparison ops
        elif token_type in ARITHMETIC_OPS:
            return self.perform_it_assign()
        elif token_type in COMPARISON_OPS or token_type in LOGIC_OPS or token_type in INF_LOGIC_OPS or token_type== "NOT_Boolean_Operation":
            return self.perform_it_assign()
        elif token_type in LITERALS:
            return self.perform_it_assign()
        
        # variable assignment
        elif token_type == "Variable_Identifier":
            if self.is_linebreak(self.get_next_token()) == False:
                if self.get_next_token()[1] == "R_Variable_Assignment":
                    return self.perform_r_assign()
                elif self.get_next_token()[1] == "IS_NOW_A_Typecasting_Operation":
                    return self.perform_is_now_typecast()
            else:
                return self.perform_it_assign()
            
        # todo: if statement
        elif token_type == "O_RLY_If-then_Keyword":
            return self.perform_orly()

        elif token_type == "O_RLY_If-then_Keyword":
            return self.perform_if_statement()
        elif token_type == "WTF_Switch-Case_Keyword":
            return self.perform_switch_case()
        elif token_type == "IM_IN_YR_Loop_Keyword":
            return self.perform_loop()
        # removed placed to start of loop evaluation
        # elif token_type == "HOW_IZ_I_Function_Keyword":
        #     return self.perform_function_definition()
        elif token_type == "I_IZ_Function_Call":
            return self.perform_it_assign()
        
        # if self.orly_flag == True:
        #     if token_type == 'YA_RLY_If-then_Keyword':
        #         # expect linebreak
        #         # check condition
        #         # savestate?
        #         pass
        #     elif token_type == "MEBBE":
        #         #expect op + linebreak
        #         # check condition
        #         # savestate?
        #         pass
        #     elif token_type == "NO WAI":
        #         # expect linebreak
        #         #check condition
        #         # savestate?
        #         pass

        else:
            return self.error("Unexpected statement")
        #Todo need to have an error for checking next token linebreak:

    """
        Handle VISIBLE statement.
    """
    def perform_visible(self):
        print(f"@VISIBLE token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        self.advance()
        print(f"@VISIBLE 2 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        output = []
        while self.current_token and self.current_token[1] != "LINEBREAK":
            # check if next expression has a + sing output delimiter
            if output and self.current_token[1] != "+_Output_Delimiter":
                return self.error("Expected plus sign (+)")
            elif output and self.current_token[1] == "+_Output_Delimiter":
                self.advance() # skip + output delimiter


            value_error = self.perform_expression()
            print(f"@VISIBLE token: L-{self.line_number} N-{self.token_index}  {self.current_token} value error: {value_error}")
            if value_error[1] == ERROR_RES:
                print("this activated")
                return value_error[0]
            
            value, var_type = value_error[0]
            # if var_type == "TROOF_Literal":
            #     return self.error("Invalid Yarn Typcasting")
            value_str = self.toStr_convert(value, var_type)

            output.append(value_str) #append YARN
            print(f"@VISIBLE 3 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
            self.advance() # move to next token
            print(f"@VISIBLE 4 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        self.console.append("".join(output))
        # print(f"@VISIBLE special token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        # return self.error("NIGHTMARE ERROR")

    """
        Get user input
    """
    def perform_gimmeh(self):
        self.advance() #skip GIMMEH
        error = self.expect_tokenType("Variable_Identifier")
        if error:
            return error
        # check if the variable is already declared
        if self.current_token[0] not in self.symbol_table:
            return self.error(f"Variable '{self.current_token[0]}' is not declared")
        
        self.console.append(f"Enter a value for {self.current_token[0]}:")
        user_input = self.gui.get_input_from_user()
        self.symbol_table[self.current_token[0]] = {"value": f'"{user_input}"', "type": "String_Literal"} 
        
        # check if linebreak is there
        self.advance()
        error = self.expect_linebreak()
        if error:
            return error


    """
        I HAS A variable_name #Declaration
    """
    def perform_assign(self):
        self.advance() # skip I_HAS_A
        if self.current_token[1] != "Variable_Identifier":
            return self.error("Expected variable name after 'I HAS A'")
        var_name = self.current_token[0]

        # check if the variable is already declared
        if var_name in self.symbol_table:
            return self.error(f"Variable '{var_name}' is already declared")
        
        value = 'NOOB' # init empty
        var_type = 'Void_Literal'
        self.advance() # move to value

        # Option variable has a value assigned
        if self.current_token and self.current_token[1] == "ITZ_Variable_Assignment":
            self.advance()
            value_error = self.perform_expression()
            # value_error should be (VALID VALUE | ERROR MESSAGE)
            if value_error[1] == ERROR_RES:
                return value_error[0]
            else:
                # value = value_error[0][0]
                value, var_type = value_error[0]
                self.advance()

        # expect_linebreak to signify the end
        error = self.expect_linebreak()
        if error:
            return error
        
        # if no error to return then update symbol table and return nothing 
        # self.symbol_table[var_name] = value
        # self.symbol_table["IT"] = value  # update implicit variable
        self.symbol_table[var_name] = {"value": value, "type": var_type} 
        self.symbol_table["IT"] = {"value": value, "type": var_type} 
        # insert code to display show in terminal
        

    """
        Parse variable assignment with 'R'.
        The equivalent to equating the variable to another lefthand value
    """
    def perform_r_assign(self):
        print(f"@r-assign 0 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        var_name = self.current_token[0]
        # check if the variable is already declared
        if self.current_token[0] not in self.symbol_table:
            return self.error(f"Variable '{self.current_token[0]}' is not declared")
        

        self.advance()
        print(f"@r-assign 1 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")

        if self.current_token[1] != "R_Variable_Assignment":
            return self.error("Expected 'R' for assignment")
        self.advance()

        # get value
        value_error = self.perform_expression()
        if value_error[1] == ERROR_RES:
            return value_error[0]
        
        print(f"@r-assign result: {value_error}")
        
        #update symbol table
        self.symbol_table[var_name] = {"value": value_error[0][0], "type": value_error[0][1]} 

        # end in linebreak 
        self.advance()
        error = self.expect_linebreak()
        if error:
            return error

    def perform_is_now_typecast(self):
        var_name = self.current_token[0]
        # check if the variable is already declared
        if self.current_token[0] not in self.symbol_table:
            return self.error(f"Variable '{self.current_token[0]}' is not declared")
        # extract variable's value
        variable_info = self.symbol_table[var_name] 
        value = variable_info["value"] 
        value_type = variable_info["type"] 
        
        # get token confirmation
        self.advance()
        if self.current_token[1] != "IS_NOW_A_Typecasting_Operation":
            return self.error("Expected IS_NOW_A_Typecasting_Operation for assignment")
        
        # get typecast
        self.advance()
        if self.current_token[1] != "Type_Literal":
            return self.error("Expected type literal for typecasting")
        to_typecast = self.current_token[0]

        if to_typecast == 'NUMBAR' or to_typecast == 'NUMBR':
            if value_type == 'NUMBAR_Literal' or value_type == "NUMBR_Literal":
                result = f'{self.arithmetic_convert((value, f'{to_typecast}_Literal'))}'
            else:
                result = f'{self.arithmetic_convert((value, value_type))}'

        elif to_typecast == 'TROOF':
            result = self.troof_convert((value, value_type))
        elif to_typecast == 'YARN':
            result = self.toStr_convert(value, value_type)
        else:
            return self.error("Invalid typecast literal")
        
        if result is None:
            return self.error("Typecast failed")
        
        #update symbol table
        self.symbol_table[var_name] = {"value": result, "type": f'{to_typecast}_Literal'} 

        # end in linebreak 
        self.advance()
        error = self.expect_linebreak()
        if error:
            return error



    """
        Any valid single operation that returns a value is added to the IT variable
        From an operation, to a literal, to a valid variable, return value from function
    """
    def perform_it_assign(self):
        value_error = self.perform_expression()
        print("IT printing state before")
        self.printState()
        print(f"value_error sa it {value_error}")
        if value_error[1] == ERROR_RES:
            return value_error[0]
        else:
            #update implicit IT variable
            # self.symbol_table["IT"] = value_error[0]
            self.symbol_table["IT"] = {"value": value_error[0][0], "type": value_error[0][1]} 
            self.printState()
            # end in linebreak 
            self.advance()
            error = self.expect_linebreak()
            if error:
                return error
            # return None

    """
        Parse arithmetic, boolean, concatenation, and typecasting, function call
        expression is the lefthandside calculation

        must check linebreak but not end self.current_token as linebreak
    """
    def perform_expression(self):

        if self.current_token[1] in LITERALS:
            value = self.current_token
            return value, OK
        
        elif self.current_token[1] == "Variable_Identifier":
            # Check if the variable exists in the symbol table
            var_name = self.current_token[0]
            if var_name not in self.symbol_table:
                return self.error(f"Undeclared variable '{var_name}'"), ERROR_RES
            # Retrieve the value of the variable
            variable_info = self.symbol_table[var_name] 
            value = variable_info["value"] 
            value_type = variable_info["type"] 
            return (value, value_type), OK

        elif self.current_token[1] in ARITHMETIC_OPS:
            value_error= self.perform_arithmetic_expression()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                return value_error[0], OK
            
        elif self.current_token[1] in LOGIC_OPS:
            value_error= self.perform_logic_expression()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                return value_error[0], OK
        elif self.current_token[1] in INF_LOGIC_OPS:
            if self.inf_logic_statement == False:
                value_error= self.perform_inf_logic_expression()
                if value_error[1] == ERROR_RES:
                    return value_error
                else:
                    return value_error[0], OK
            else:
                return self.error(f"No Nested infinite logic operators"), ERROR_RES
        elif self.current_token[1] in COMPARISON_OPS:
            value_error= self.perform_comparison_expression()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                return value_error[0], OK
            
        elif self.current_token[1] == "NOT_Boolean_Operation":
            value_error= self.perform_not()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                return value_error[0], OK
            
        elif self.current_token[1] == "SMOOSH_String_Contatenation":
            value_error= self.perform_smoosh()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                print(f"smoosh valer {(f'"{value_error}"', 'String_Literal')}")
                return value_error[0], OK
        
        elif self.current_token[1] == "MAEK_Typecasting_Operation":
            value_error= self.perform_maek()
            if value_error[1] == ERROR_RES:
                return value_error
            else:
                return value_error[0], OK
        
        elif self.current_token[1] == "I_IZ_Function_Call":
            value_error= self.perform_function_call()

            if value_error[1] == ERROR_RES:

                return value_error
            else:
                return value_error[0], OK
        else:
            return self.error("Invalid expression"), ERROR_RES

    """
        Compute arithmetic expressions.
        second arguement OK for success
        else second arguement ERROR_RES for unsuccesful expression
    """
    def perform_arithmetic_expression(self):
        float_flag = False # True when result must return a float
        opname=self.current_token[1]
        operation = ARITHMETIC_OPS[opname] #get the operation

        # evaluate operand1
        self.advance()
        operand1 = self.perform_expression()
        if operand1[1] == ERROR_RES: 
            return operand1
        
        #ensure AN token is available
        self.advance()

        error = self.expect_tokenType('AN_Parameter_Delimiter')
        if error:
            return error, ERROR_RES

        # evaluate operand2
        self.advance()
        operand2 = self.perform_expression()
        if operand2[1] == ERROR_RES: 
            return operand2

        #check if operand1's value is valid: not NONE (or no error in parsing)
        # if operand1[1] == ERROR_RES or operand2[1] == ERROR_RES:
        #     return self.error("Undefined operand"), ERROR_RES
        
        #check if either operand has NUMBAR / float
        if operand1[0][1] == "NUMBAR_Literal" or operand2[0][1] == "NUMBAR_Literal":
            float_flag = True
            
        operand1 = self.arithmetic_convert(operand1[0])
        operand2 = self.arithmetic_convert(operand2[0])
        # if there is still an invalid vlaue for arithmetic conversion
        print(f"op1--{operand1} and op2--{operand2}")
        if operand1 is None or operand2 is None:
            return self.error("Invalid operand type"), ERROR_RES
        
        if isinstance(operand1, float) or isinstance(operand2,float):
            float_flag = True
        
        result = operation(operand1,operand2)
        print(f'result of arith{opname} op1{operand1} op1{operand2}=={result}')
        if float_flag==True:
            return (f'{float(result)}', "NUMBAR_Literal"), OK
        else:
            return (f'{int(result)}', "NUMBR_Literal"), OK
        
    """
        Implicit typecasting for arithmetic operations
        Parameters value (The token form) returns only the value needed to be computed
        else return None (ma-catch yung NOOB or any other tokentype)
    """
    def arithmetic_convert(self,value):
        if value[1] == "TROOF_Literal":
            if value[0] == "WIN":
                return 1
            else:
                return 0
        elif value[1] == "String_Literal":
            to_num = value[0][1:-1]
            try:
                if '.' in to_num:
                    to_num = float(to_num) 
                else: 
                    to_num = int(to_num)
                return to_num
            except ValueError:
                return None
        elif value[1] == "NUMBAR_Literal":
            return float(value[0])
        elif value[1] == "NUMBR_Literal":
            return int(value[0])
        else:
            return None

    """
        Implicit typecasting for VISIBLE and SMOOSH (Yarn operations)
    """
    def toStr_convert(self,value, var_type):
        if var_type == "String_Literal":
            return value[1:-1]
        elif var_type == "NUMBAR_Literal":
            number_float = float(value)
            rounded_number = round(number_float, 2)
            return f'{rounded_number:.2f}'
        elif var_type == "NUMBR_Literal":
            return f'{int(value)}'
        elif var_type == "Void_Literal":
            return ''
        elif var_type == "TROOF_Literal":
            if value == 'FAIL':
                # return '' #notsure: typecast
                return value
            else:
                return value
        else:
            return None
    
    """
        automatic troof conversion
    """
    def troof_convert(self,value):
        print(f"pasok: {value}")
        if value[1] == "String_Literal":
            str = value[0][1:-1]
            if str == '':
                return 'FAIL'
            else: 
                return 'WIN'
        elif value[1] == "NUMBAR_Literal" or value[1] == "NUMBR_Literal":
            if value[0] == 0:
                return 'FAIL'
            else:
                return 'WIN'
        elif value[1] == "Void_Literal":
            return 'FAIL'
        elif value[1] == "TROOF_Literal":
            return value[0]
        else:
            return None

    """
        perform logical expressions
        Needs Troof as operands
    """
    def perform_logic_expression(self):
        opname=self.current_token[1]
        operation = LOGIC_OPS[opname] #get the operation

        # evaluate operand1
        self.advance()
        operand1 = self.perform_expression()
        if operand1[1] == ERROR_RES:
            return operand1
        
        #ensure AN token is available
        self.advance()
        error = self.expect_tokenType('AN_Parameter_Delimiter')
        if error:
            return error, ERROR_RES

        # evaluate operand2
        self.advance()
        operand2 = self.perform_expression()
        if operand2[1] == ERROR_RES: 
            return operand2
        
        # get troof values, convert to troof if necessary
        troofed1 = operand1[0][0] if operand1[0][1]=='TROOF_Literal' else self.troof_convert(operand1[0])
        troofed2 = operand2[0][0] if operand2[0][1]=='TROOF_Literal' else self.troof_convert(operand2[0])
        print(f"troof1 {troofed1} and troof2 {troofed2}")

        # if result is none aka cannot be typecast into troof, send error
        if troofed1 is None or troofed2 is None:
            return self.error("Invalid troof operand type"), ERROR_RES
        
        result = operation(troofed1,troofed2)
        print(f'result of troof({opname}) op1[{operand1} - {troofed1}] op2[{operand2} - {troofed2}]== {result}')
        if result == True:
            return ('WIN', "TROOF_Literal"), OK
        elif result == False:
            return ('FAIL', "TROOF_Literal"), OK

    """
        infinite boolean
        not allowed to have nested of it but as long as its operands are troof values    
    """
    def perform_inf_logic_expression(self):
        opname=self.current_token[1]
        operation = INF_LOGIC_OPS[opname] #get the operation

        self.advance()
        # evaluate the operands
        troof_values = []
        while self.current_token and self.current_token[1] != 'MKAY_Concatenation_Delimiter' and self.current_token[1] != "LINEBREAK":
            if troof_values and self.current_token[1] == "AN_Parameter_Delimiter":
                self.advance() # skip AN
            elif self.current_token[1] == "AN_Parameter_Delimiter" and troof_values != []:
                return self.error("Invalid AN keyword"), ERROR_RES
            
            
            operand = self.perform_expression()
            if operand[1] == ERROR_RES:
                return operand
            
            print(f"curr inf op: {operand}")
            # implicitly typecast
            troofed = operand[0][0] if operand[0][1]=='TROOF_Literal' else self.troof_convert(operand[0])
            # if result is none aka cannot be typecast into troof, send error
            if troofed is None:
                return self.error("Invalid troof operand type"), ERROR_RES 
            troof_values.append(troofed)
            self.advance() # continue loop
        if self.current_token[1] != "MKAY_Concatenation_Delimiter":
            return self.error("Syntax Error: Missing MKAY at infinite logic operator"), ERROR_RES
        
        if len(troof_values) == 0:
            return self.error("Syntax Error: Empty operand list for infinite logic operator"), ERROR_RES

        
        result = operation(troof_values)
        print(f'result of troof({opname}) op1[{operand} - {troof_values}] \n======> {result}')
        if result == True:
            return ('WIN', "TROOF_Literal"), OK
        elif result == False:
            return ('FAIL', "TROOF_Literal"), OK
        
          
    """
        returns the opposite value
    """
    def perform_not(self):
        self.advance() # skip NOT
        value_error = self.perform_expression()
        if value_error[1] == ERROR_RES:
            return value_error[0], ERROR_RES
        print(f"levalue: {value_error}")
        troofed = self.troof_convert(value_error[0])
        print(f"letroof: {troofed}")
        if troofed == 'WIN':
            return ('FAIL', 'TROOF_Literal'), OK
        elif troofed == 'FAIL':
            return ('WIN', 'TROOF_Literal'), OK
        else:
            return self.error("Invalid type for NOT operator"), ERROR_RES
        
    """
        Handle string concatenation with 'SMOOSH'.
    """        
    def perform_smoosh(self):
        result = []
        
        while self.get_next_token() and self.get_next_token()[1] != "LINEBREAK":
            self.advance() # move to next token
            # check if next expression has a + sing result delimiter
            if result and self.current_token[1] != "AN_Parameter_Delimiter":
                return self.error("expected AN parameter"), ERROR_RES
            elif result and self.current_token[1] == "AN_Parameter_Delimiter":
                self.advance() # skip + output delimiter

            value_error = self.perform_expression()
            if value_error[1] == ERROR_RES:
                return value_error
            
            value, var_type = value_error[0]
            # if var_type == "TROOF_Literal":
            #     return self.error("Invalid Yarn Typcasting")

            value_str = self.toStr_convert(value, var_type)

            result.append(value_str) #append YARN
            
        if len(result) <2:
            return self.error("Expected at least 2 strings to smoosh"), ERROR_RES
        else:
            return (f'"{"".join(result)}"', 'String_Literal'), OK
        

    """
        Handle typecasting with 'MAEK'.
    """
    def perform_maek(self):
        print(f"@MAEK 0 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")
        self.advance() # skip MAEK
        
        
        print(f"@MAEK 1 token: L-{self.line_number} N-{self.token_index}  {self.current_token}")

        if self.current_token[1] == "A_Typecasting_Operation":
            self.advance() # skip suplemental 'A' token

        value_error = self.perform_expression()
        # value_error should be (VALID VALUE | ERROR MESSAGE)
        if value_error[1] == ERROR_RES:
            return value_error[0]
        value, value_type = value_error[0]
        # error = self.expect_tokenType("A_Typecasting_Operation")
        # if error:
        #     return error
        
        # get typecast
        self.advance()
        if self.current_token[1] != "Type_Literal":
            return self.error("Expected type literal for typecasting"), ERROR_RES
        to_typecast = self.current_token[0]

        if to_typecast == 'NUMBAR' or to_typecast == 'NUMBR':
            if value_type == 'NUMBAR_Literal' or value_type == 'NUMBR_Literal':
                print(f"mein value={value} and vtype={value_type}")
                result = f'{self.arithmetic_convert((value, f'{to_typecast}_Literal'))}'
            else:
                print(f"mine value={value} and vtype={value_type}")
                result = f'{self.arithmetic_convert((value, value_type))}'
                print(f"mine result: {result}")

        elif to_typecast == 'TROOF':
            result = self.troof_convert((value, value_type))
        elif to_typecast == 'YARN':
            result = self.toStr_convert(value, value_type)
        else:
            return self.error("Invalid typecast literal"), ERROR_RES
        
        if result is None:
            return self.error("Typecast failed"), ERROR_RES
        # return MAEK value
        return (result, f"{to_typecast}_Literal"), OK
    
    """
        perform comparison expressions returns WIN OR FAIL
        operands can be NUMBR or NUMBAR as long as both match, no automatic typecasting
    """
    def perform_comparison_expression(self):
        opname=self.current_token[1]
        operation = COMPARISON_OPS[opname] #get the operation
        print(f"comparison opname: {opname}")
        # evaluate operand1
        self.advance()
        operand1 = self.perform_expression()
        if operand1[1] == ERROR_RES:
            return operand1
        elif operand1[0][1] != 'NUMBR_Literal' and operand1[0][1] != 'NUMBR_Literal': #check if operand1 is NUMBR or NUMBAR
            return self.error("Comparison only allowed for arithmetic values"), ERROR_RES
        
        #ensure AN token is available
        self.advance()
        error = self.expect_tokenType('AN_Parameter_Delimiter')
        if error:
            return error, ERROR_RES

        # evaluate operand2
        self.advance()
        operand2 = self.perform_expression()
        if operand2[1] == ERROR_RES: 
            return operand2
        elif operand2[0][1] != 'NUMBR_Literal' and operand2[0][1] != 'NUMBR_Literal': #check if operand1 is NUMBR or NUMBAR
            return self.error("Comparison only allowed for arithmetic values"), ERROR_RES
        
        # check if values have the same type
        if operand1[0][1] != operand2[0][1]:
            return self.error("Comparisons must have the same type"), ERROR_RES

        print(f"op1-- {operand1[0]} and op2-- {operand2[0]}")
        operand1 = self.arithmetic_convert(operand1[0])
        operand2 = self.arithmetic_convert(operand2[0])

        
        result = operation(operand1,operand2)
        print(f'result of comparison {opname} op1({operand1}) op2({operand2}) == {result}')
        if result == True:
            return ('WIN', "TROOF_Literal"), OK
        elif result == False:
            return ('FAIL', "TROOF_Literal"), OK
    """
        Handle IF-THEN
    """
    def perform_orly(self):
        pass
    #     self.advance() # skip ORLY
    #     error = self.expect_linebreak() # ORLY must be stand alone
    #     if error:
    #         return error
        
    #     self.skipLine()
    #     # ==== parse the if-then block =====
    #     # flags
    #     has_yarly=False
    #     has_nowai=False
    #     has_mebbe=False
    #     is_collecting=False

    #     self.orly_flag = True
    #     condtion_blocks = []

    #     #save state

    #     while self.current_token and self.current_token[1] != 'OIC_If-then_Keyword' and self.current_token[1] != "KTHXBYE_Code_Delimiter":
    #         # todo loop to get body
    #         if is_collecting == True and self.current_token[1] != 'YA_RLY_If-then_Keyword'  and self.current_line[1] != 'MEBBE_If-then_Keyword' 'YA_RLY_If-then_Keyword':
    #             error = self.statement()
    #             if error:
    #                 return self.error("Semantic error: Invalid statement in loop"), ERROR_RES
                

    #         elif self.current_token[1] == 'YA_RLY_If-then_Keyword':
    #             if is_collecting == True:
    #                 return self.error("Invalid YA RLY"), ERROR_RES
    #             if has_yarly == True:
    #                 return self.error("No more than 1 YA RLY per O RLY block"), ERROR_RES
    #             if has_mebbe == True or has_nowai == True:
    #                 return self.error("YA RLY is before MEBBE and NO WAI"), ERROR_RES

    #             self.advance()
    #             error = self.expect_linebreak() # YARLY must be stand alone
    #             if error:
    #                 return error
    #             has_yarly = True
    #             # check conditioin
    #             # todo IT check WIN typecast if true then is_collection == True
    #             is_collecting=True
                
            
    #         elif self.current_token[1] == 'NO_WAI_If-then_Keyword' and has_nowai==False and has_yarly==True:
    #             self.advance()
    #             error = self.expect_linebreak() # NO WAI must be stand alone
    #             if error:
    #                 return error
    #             has_yarly = True
    #             is_collecting=True
             
    #             condtion_blocks.append({'cond': 'NO_WAI_If-then_Keyword', 'body': [], 'line': self.line_number})
            
    #         elif self.current_token[1] == 'MEBBE_If-then_Keyword':
    #             if is_collecting == True:
    #                 # save state 
    #                 is_collecting == False
    #             if has_yarly == False:
    #                 return self.error("Error: Mebbe after YA RLY"), ERROR_RES
    #             if has_nowai == True :
    #                 return self.error("Errpr: Mebbe befpre NO WAI"), ERROR_RES

    #             self.advance()
        
    #             is_collecting=True


    #         elif is_collecting == False:
    #             pass

    #         self.advance() # continue while-loop


    #     # todo end in OIC check

                
                
                
                
                

        
    #     # save state
    #     self.saveState()

    # def getLine(self):
    #     line = []
    #     while self.current_token and self.current_token!= ""

        

    """
        Parse function definition using 'HOW IZ I'.
    """
    def perform_function_definition(self):
        self.advance()  # Skip 'HOW IZ I'
        error = self.expect_tokenType("Variable_Identifier")
        if error:
            return error
        func_name = self.current_token

        # check if the variable is already declared
        if func_name in self.symbol_table:
            return self.error(f"Function signature '{func_name}' is already defined")
        
        
        # Parse the parameter list 
        self.advance()
        parameters = { "IT": {"value": 'NOOB', "type": "Void_Literal"} } 
        count_param=0
        
        #return self.error("ERROR HERE 2023")
        while self.current_token[1] != 'LINEBREAK':
            if self.current_token[1]=="YR_Parameter_Delimiter":
                self.advance()
                # make sure next token is the variable identifier for parameter
                param_error = self.expect_tokenType("Variable_Identifier")
                if param_error:
                    return param_error
                # check to avoid variable_identifier confusion
                if self.current_token[0] in self.symbol_table:
                    return self.error(f"Function parameter '{self.current_token[0]}' is already  in global")
                # add to local symbol_table
                parameters[self.current_token[0]] = {"value": 'NOOB', "type": count_param}
                count_param += 1 #increment
            self.advance()
        
        starting_line = self.line_number + 1 # save starting line of body
        self.skipLine()

        

        # get function body tokens
        # todo actually check if the statements in function declaration are correct, currently can only be detected during function call
        body = []

        while self.current_token and self.current_token[1] != "IF_U_SAY_SO_Function_Keyword":
            body.append(self.current_token)
            self.advance()
        if self.current_token[1] !="IF_U_SAY_SO_Function_Keyword":
            return self.error("Function Definition is missing 'IF_U_SAY_SO_Function_Keyword'")
            
        body.append(self.current_token) # append 'IF_U_SAY_SO_Function_Keyword'

        # add function to the symbol_table
        self.symbol_table[func_name[0]] = {"value": {"params": parameters, "body": body}, "type": "Function_Signature", "body_line" : starting_line} #added type not in lexical analysis

        # check if linebreak is there
        self.advance()
        error = self.expect_linebreak()
        if error:
            return error
        # end of perform_function_definition

    """
        Parse function call using 'I IZ'.
    """
    def perform_function_call(self):
        self.advance() # skip I IZ token

        error = self.expect_tokenType("Variable_Identifier")
        if error:
            return error
        func_name = self.current_token[0]

        

        # check if the variable is already declared
        if func_name not in self.symbol_table:
            return self.error(f"Function '{func_name}' is not declared"), ERROR_RES

        
        # check if variable_identifier is a function afterall
        func_data = self.symbol_table[func_name]
        if func_data["type"] != "Function_Signature": 
            return self.error(f"'{func_name}' is not a function"), ERROR_RES
        
        
        
        # get function parameters and body 
        parameters = func_data["value"]["params"] 
        print(f"parameters: {parameters}")
        body = func_data["value"]["body"]
        parameter_num = len(parameters) - 1 # minus 1 due to the implici 'IT'
        starting_line = func_data["body_line"]

        # get arguements
        self.advance()
        param_count = 0
        first_param=True
        print(f"FUNCTION CALL OBER ERE 2")
        # assume YR is the start
        print(f'The current token: {self.current_token} goto loop?({self.line_number})')
        if self.current_token[1] == 'YR_Parameter_Delimiter':
            while (self.current_token[1] != 'LINEBREAK' and self.current_token[1] !='MKAY_Concatenation_Delimiter') and param_count<parameter_num:
                if self.current_token[1] =="YR_Parameter_Delimiter" and first_param == False:
                    return self.error("Invalid YR_Parameter"), ERROR_RES
                if self.current_token[1] =="YR_Parameter_Delimiter" and first_param == True:
                    first_param= False
                elif self.current_token[1] == "AN_Parameter_Delimiter" and first_param == False:
                    self.advance()
                elif self.current_token[1] == "AN_Parameter_Delimiter" and first_param == True:
                    return self.error("Invalid AN keyword"), ERROR_RES
                # get parameter value
                self.advance()
                value_error = self.perform_expression()
                if value_error[1] == ERROR_RES:
                    print(f"value error: {value_error}")
                    return  self.error("Invalid value for function parameter"), ERROR_RES
                value_param, value_type = value_error[0]

                # get parameters value
                for key, value in parameters.items():
                    if value.get("type") == param_count:
                        value["value"] = value_param
                        value["type"] = value_type
                self.advance()
                param_count += 1

        
        # check if mkay is present
        
        if self.current_token[1] != 'MKAY_Concatenation_Delimiter':
            return self.error("Expected MKAY at the end of function call"), ERROR_RES
        # if self.is_linebreak(self.get_next_token()) == False:
        #     return self.error("Expected linebreak after MKAY at the end of function call"), ERROR_RES
        

        for key, value in parameters.items(): 
            if key != "IT" and value["value"] == "NOOB": 
                print(f"Entry {key} has 'NOOB' value")
                return self.error(f"'NOOB value' arguement for {key}"), ERROR_RES
            
        # save state -- copy of original symbol table, tokens
        #local_stable = original_stable | parameters # combine symbol table with the parameters for local symbol table
        self.saveState()

        # update current state when evaluating body
        # self.symbol_table = parameters
        # for functions to acces global variables
        self.symbol_table = self.symbol_table | parameters
        self.tokens = body
        self.token_index = 0
        self.current_token = self.tokens[0]
        self.line_number = starting_line
        self.inside_function = True

        # evaluate function body
        return_value = ('NOOB', 'Void_Literal')
        print(f'The current token: {self.current_token} bro1? line({self.line_number})')
        self.skipLine()
        print(f'The current token: {self.current_token} bro2? line({self.line_number})')
        while self.current_token and self.current_token[1] != 'IF_U_SAY_SO_Function_Keyword':
            print(f'in function current token: {self.current_token}??? line({self.line_number})')
            if self.current_token[1] == 'GTFO_Return_Keyword': # todo add validation check in if-else
                break
            elif self.current_token[1] == 'FOUND_YR_Return_Keyword': #todo  add validation check  in all control-flow  # check with is function flag
                # get expression value
                self.advance()
                value_error = self.perform_expression()
                print("VALUE ERROR FUNC:")
                print(value_error)
                if value_error[1] == ERROR_RES:
                    return value_error[0], ERROR_RES
                return_value = value_error[0]
                break
            else:              
                error = self.statement()
                if error:
                    return error
                self.skipLine()

        print(f'The current token: {self.current_token} whu huppen? line({self.line_number})')
        
        # restore state 
        self.restoreState()
        print("Return value")
        print(return_value)
        return return_value, OK


    """
        save the state data
        push to stack
    """
    def saveState(self) :
        saved_state = { "symbol_table": self.symbol_table, 
                       "token_index": self.token_index,
                       "line_number": self.line_number,
                       "current_line": self.current_line,
                       "tokens": self.tokens,
                       "current_token" : self.current_token,
                       "inside_function": self.inside_function } 
        self.functions_stack.append(saved_state)
    """
        restore state data
        pop stack
    """
    def restoreState(self):
        previous_state = self.functions_stack.pop() 
        self.symbol_table = previous_state["symbol_table"] 
        self.token_index = previous_state["token_index"]
        self.tokens = previous_state["tokens"]
        self.line_number = previous_state["line_number"]
        self.current_line = previous_state["current_line"]
        self.current_token = previous_state["current_token"]
        self.inside_function = previous_state["inside_function"]

    def printState(self):
        print("Printing state........")
        print(f"s-currtoken: {self.current_token}")
        print(f"s-current line: {self.line_number}")
        print(f"s- symbol table {self.symbol_table}")

    # def perform_loop(self):
    #     loop


        


        
