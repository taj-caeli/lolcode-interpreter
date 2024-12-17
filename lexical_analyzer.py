import re

BAD_VARIABLE_NAMES = ["OBTW", "TLDR", "BTW"] # avoid regex assigning a reserved keyword as a variable
LEX_ERROR = -1

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.token_patterns = {
        r'\s*HAI\s*': 'HAI_Code_Delimiter',
        r'\s*KTHXBYE\s*': 'KTHXBYE_Code_Delimiter',
        r'\s*WAZZUP\s*': 'WAZZUP_Variable_Declaration_Delimiter',
        r'\s*BUHBYE\s*': 'BUHBYE_Variable_Declaration_Delimiter',
        # r'\s*TLDR\s+': 'Comment Delimiter',
        # r'((\s*^BTW.*)|(^BTW.*)|(\s*^OBTW.*)|(^OBTW.*))': 'Comment Line',
        # r'\s*^BTW .*': 'Comment Line',
        # r'\s*\bBTW\b.*\s*': 'Comment',  # match 'BTW' and the rest of the line as a comment
        # r'\s*\bOBTW.*TLDR\b.*\s*': 'Comment', 
        r'\s*I HAS A\s+': 'I_HAS_A_Variable_Declaration',
        r'\s*ITZ\s+': 'ITZ_Variable_Assignment',
        r'\s*R\s+': 'R_Variable_Assignment',
        r'\s*AN\s+': 'AN_Parameter_Delimiter',                                   
        r'\s*SUM OF\s+': 'SUM_OF_Arithmetic_Operation',
        r'\s*DIFF OF\s+': 'DIFF_OF_Arithmetic_Operation',
        r'\s*PRODUKT OF\s+': 'PRODUKT_OF_Arithmetic_Operation',
        r'\s*QUOSHUNT OF\s+': 'QUOSHUNT_OF_Arithmetic_Operation',
        r'\s*MOD OF\s+': 'MOD_OF_Arithmetic_Operation',
        r'\s*BIGGR OF\s+': 'BIGGR_OF_Arithmetic_Operation',
        r'\s*SMALLR OF\s+': 'SMALLR_OF_Arithmetic_Operation',
        r'\s*BOTH OF\s+': 'BOTH_OF_Boolean_Operation',
        r'\s*EITHER OF\s+': 'EITHER_OF_Boolean_Operation',
        r'\s*WON OF\s+': 'WON_OF_Boolean_Operation',
        r'\s*NOT\s+': 'NOT_Boolean_Operation',
        r'\s*ANY OF\s+': 'ANY_OF_BooleanOperation',
        r'\s*ALL OF\s+': 'ALL_OF_Boolean_Operation',
        r'\s*BOTH SAEM\s+': 'BOTH_SAEM_Comparison_Operation',
        r'\s*DIFFRINT\s+': 'DIFFRINT_Comparison_Operation',
        r'\s*SMOOSH\s+': 'SMOOSH_String_Contatenation',
        r'\s*MAEK\s+': 'MAEK_Typecasting_Operation',
        r'\s*A\s+': 'A_Typecasting_Operation',                   
        r'\s*IS NOW A\s+': 'IS_NOW_A_Typecasting_Operation', #changed from A_Typecasting_Operation
        r'\s*VISIBLE\s+': 'VISIBLE_Output_Keyword',
        r'\s*\+\s+': '+_Output_Delimiter',
        r'\s*GIMMEH\s+': 'GIMMEH_Input_Keyword',
        r'\s*O\sRLY\?\s*': 'O_RLY_If-then_Keyword',
        r'\s*YA RLY\s*': 'YA_RLY_If-then_Keyword',
        r'\s*MEBBE\s+': 'MEBBE_If-then_Keyword',
        r'\s*NO WAI\s*': 'NO_WAI_If-then_Keyword',
        r'\s*OIC\s*': 'OIC_If-then_Keyword',
        r'\s*WTF\?\s*': 'WTF_Switch-Case_Keyword',
        r'\s*OMG\s+': 'OMG_Switch-Case_Keyword',
        r'\s*OMGWTF\s*': 'OMGWTF_Switch-Case_Keyword',
        r'\s*IM IN YR\s+': 'IM_IN_YR_Loop_Keyword',
        r'\s*UPPIN\s+': 'UPPIN_Loop_Operation',
        r'\s*NERFIN\s+': 'NERFIN_Loop_Operation',
        r'\s*YR\s+': 'YR_Parameter_Delimiter',
        r'\s*TIL\s+': 'TIL_Loop_Keyword',
        r'\s*WILE\s+': 'WILE_Loop_Keyword',
        r'\s*IM OUTTA YR\s+': 'IM_OUTTA_YR_Loop_Keyword',
        r'\s*HOW IZ I\s+': 'HOW_IZ_I_Function_Keyword',
        r'\s*IF U SAY SO\s*': 'IF_U_SAY_SO_Function_Keyword',
        r'\s*GTFO\s*': 'GTFO_Return_Keyword',
        r'\s*FOUND YR\s+': 'FOUND_YR_Return_Keyword',
        r'\s*I IZ\s+': 'I_IZ_Function_Call',
        r'\s*MKAY\s*': 'MKAY_Concatenation_Delimiter',                              
        r'\s*NOOB\s+': 'Void_Literal',

        # Literals and variable identifiers
        r'\s*(NUMBR|NUMBAR|YARN|TROOF|NOOB)\s?': 'Type_Literal',  
        r'\s*(WIN|FAIL)\s*': 'TROOF_Literal',                 
        r'\s*\"[^\"]*\"\s*': 'String_Literal',
        r'\s*[a-zA-Z_][a-zA-Z0-9_]*\s*': 'Variable_Identifier',
        r'\s*\d+\.\d+\s*': 'NUMBAR_Literal',
        r'\s*\d+\s*': 'NUMBR_Literal'
    }

    def lexical_analysis(self):
        # print(self.code)
        in_multiline_comment = None 
        sourceCodeLines = self.code.split('\n')  # Split lines to keep track of line number

        for lineNo, lineOfCode in enumerate(sourceCodeLines, start=1):  # For each line of code
            if not lineOfCode.strip():
                self.tokens.append(('linebreak', 'LINEBREAK'))
                continue

            errorInLine = 0  # Flag for error in line

            if in_multiline_comment:
                if re.match(r'\s*\bTLDR\b(\s)*$', lineOfCode):
                    in_multiline_comment = None
                    self.tokens.append(('TLDR', 'MULTILINE_COMMENT'))
                    # self.tokens.append(('linebreak', 'LINEBREAK'))
                    continue
                else:
                    self.tokens.append((lineOfCode, 'MULTILINE_COMMENT'))
                    continue
            else:
                if re.match(r'\s*\bOBTW\b(.)*', lineOfCode):
                    in_multiline_comment = lineNo
                    self.tokens.append((lineOfCode, 'MULTILINE_COMMENT'))
                    # self.tokens.append(('linebreak', 'LINEBREAK'))
                    continue

                while len(lineOfCode) != 0:
                    didMatch = 0  # Flag for matching                
                    if re.match(r'\s*\bBTW\b\s*', lineOfCode):
                        # self.tokens.append((lineOfCode.strip(), 'Comment'))
                        break

                    for pattern, token_type in self.token_patterns.items():
                        matched = re.match(pattern, lineOfCode)  # Check if matching
                        if matched:
                            if(token_type == "Variable_Identifier") and (matched.group(0).strip()) in BAD_VARIABLE_NAMES:
                                didMatch ==0
                                break
                            else:
                                didMatch = 1  # Set flag to match
                                self.tokens.append((matched.group(0).strip(), token_type))
                                lineOfCode = lineOfCode.replace(matched.group(0), '', 1).strip()
                                if len(lineOfCode) == 0:
                                    self.tokens.append(('linebreak', 'LINEBREAK'))  # Add linebreak token if \n is encountered
                                break

                    if didMatch == 0:  # If it has no match with any of the lexeme patterns
                        errorInLine = lineNo  # Set line number where error was encountered
                        break

            if errorInLine != 0:  # If error was encountered, return error
                # print("Lexical error in line " + str(errorInLine))
                self.tokens = [(LEX_ERROR, f"Lexical error at line {str(errorInLine)}")]
                return self.tokens

            # Ensure a LINEBREAK token is added if the line had content but no matches
            if len(lineOfCode) > 0:
                self.tokens.append(('linebreak', 'LINEBREAK'))

        if in_multiline_comment:
            # print(f"Lexical error (line: {in_multiline_comment}) missing TLDR MULTICOMMENT")
            self.tokens = [(LEX_ERROR, f"Lexical error at line {str(errorInLine)}")]

        return self.tokens
        # end of def lex_analysis()