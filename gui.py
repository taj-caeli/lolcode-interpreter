import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QTableWidget, QTableWidgetItem, QFileDialog, QSplitter)
from PyQt5.QtCore import Qt
#from lexical_analyzer import lexical_analysis
from lexical_analyzer import Lexer
# from newsyntax import *
from syntax import Interpreter

LEX_ERROR = -1

class LOLCodeInterpreter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LOLLLLLLLLLLLLLLLLLLLL')
        
        layout = QVBoxLayout()

        # open file button
        file_button = QPushButton('Open File')
        file_button.clicked.connect(self.load_file)
        layout.addWidget(file_button)
        
        # text editor for code
        self.text_editor = QTextEdit()
        layout.addWidget(self.text_editor)

        # split lexeme and symbol table
        splitter = QSplitter(Qt.Horizontal)

        # lexemes table
        self.lexemes_table = QTableWidget()
        self.lexemes_table.setColumnCount(2)
        self.lexemes_table.setHorizontalHeaderLabels(["Lexeme", "Classification"])
        splitter.addWidget(self.lexemes_table)

        # symbol table
        self.symbol_table = QTableWidget()
        self.symbol_table.setColumnCount(2)
        self.symbol_table.setHorizontalHeaderLabels(["Identifier", "Value"])
        splitter.addWidget(self.symbol_table)

        layout.addWidget(splitter)

        # execute button
        execute_button = QPushButton('EXECUTE')
        execute_button.clicked.connect(self.run_code)
        layout.addWidget(execute_button)

        # console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
         # layout for input box and enter button
        input_layout = QHBoxLayout()  # Horizontal layout for input box and button
        
        # input box
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("TYPE INPUT HERE")
        self.input_box.setFixedHeight(30)
        input_layout.addWidget(self.input_box)

        enter_input_button = QPushButton("ENTER INPUT")
        enter_input_button.clicked.connect(self.process_input)  # process input if clicked
        input_layout.addWidget(enter_input_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def process_input(self):
        self.user_input = self.input_box.toPlainText().strip()
        self.input_box.clear()
        self.input_ready = True

    def get_input_from_user(self):
        self.input_ready = False
        # self.console.append("Type input below!")
        while not self.input_ready:
            QApplication.processEvents()  # keep GUI responsive
        return self.user_input




    def load_file(self):
        options = QFileDialog.Options()
        # upload .lol files
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open LOLCODE File', '', 'LOLCODE Files (*.lol);;Text Files (*.txt);;All Files (*)', options=options
        )
        if file_path:
            with open(file_path, 'r') as file:
                code = file.read()
                self.text_editor.setText(code)


    def run_code(self):
        code = self.text_editor.toPlainText()
        lexer = Lexer(code)
        tokens = lexer.lexical_analysis()
        #tokens = lexical_analysis(code)

        self.console.clear()    # reset/clean up console
        self.lexemes_table.clear()

        # print(tokens)
        for token in tokens:
            print(token)

        # valid_only = tokens
        # valid_only = [item for item in valid_only if item[1] != "LINEBREAK"]

        # i = 0

        # TAJAN: Commented out
        # #used to check if OBTW-TLDR is implemented correctly by checking if each have appropriate linebreaks
        # while i < len(tokens):
        #     if (tokens[i][1] == "Start of Block Comment" and tokens[i+1][1] == "Comment") or (tokens[i][1] == "Comment" and tokens[i+1][1] == "End of Block Comment"):
        #         self.console.append("OBTW/TLDR must be standalone!")
        #     i += 1
        #     # TAJAN not sure working:
        #     # if ((tokens[i][1] == "Start of Block Comment" and tokens[i-1][1] != "LINEBREAK") or (tokens[i][1] == "Comment" and tokens[i+1][1] == "LINEBREAK" and tokens[i+2][1] == "End of Block Comment" and tokens[i+3][1] == "LINEBREAK")):
        #     #     self.console.append("OBTW/TLDR must be standalone!")
        #     #     print("console error: OBTW/TLDR must be standalone!")
        #     # i += 1

        if ( (len(tokens)==1 )and (tokens[0][0] == LEX_ERROR) ): # if there was an error in lexical analysis
            self.console.append(tokens[0][1])
        else:
            # print tokens into lexeme table in gui
            self.lexemes_table.setRowCount(len(tokens))
            for i, (lexeme, classification) in enumerate(tokens):
                self.lexemes_table.setItem(i, 0, QTableWidgetItem(lexeme))
                self.lexemes_table.setItem(i, 1, QTableWidgetItem(classification))
            
            #print(tokens) #testing in terminal
            # print(tokens)
            for token in tokens:
                print(token)

            
            # syntaxResult, stable = main(tokens, self.console, self) #performs the newsyntax main(), does the printing in newsyntax
            interpreter = Interpreter(tokens, self.console, self)
            syntaxResult, stable = interpreter.parse()

            #populate symbol table
            self.symbol_table.setRowCount(len(stable)) 
            for i, (variable, value) in enumerate(stable.items()):
                self.symbol_table.setItem(i, 0, QTableWidgetItem(variable))
                self.symbol_table.setItem(i, 1, QTableWidgetItem(str(value)))

            # self.symbol_table.setRowCount(len(stable))
            # for i, (variable, value) in enumerate(stable.items()):
            #     variable_name = variable[0] if isinstance(variable, tuple) else variable
            #     value_str = str(value["value"]) if isinstance(value, dict) else str(value)
            #     self.symbol_table.setItem(i, 0, QTableWidgetItem(variable_name))
            #     self.symbol_table.setItem(i, 1, QTableWidgetItem(value_str))


            # print(syntaxResult)
            if (syntaxResult != "Correct"): # print error and stop program
                # print(syntaxResult)
                self.console.append(syntaxResult)
            # else:
            #     self.console.append(syntaxResult)
                # continue to semantics

            # placeholder for console
            for token in tokens:
                if token[0] == 'Error':
                    self.console.append(token[0] + token[1])
                    break


app = QApplication(sys.argv)
window = LOLCodeInterpreter()
window.resize(800, 600)
window.show()
sys.exit(app.exec_())