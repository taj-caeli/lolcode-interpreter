# lolcode-interpreter

## Setup for my UBUNTU pc

1. **Create a virtual environment** in the project directory:
   ```bash
   python3 -m venv venv
   ```
2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```
3. **Install `PyQt5` within the virtual environment**:
   ```bash
   pip install PyQt5
   ```
4. **Run your script** within the virtual environment:
   ```bash
   python gui.py
   ```
### gitignore content

```
#ignoring generated python cache files on ubuntu
__pycache__/
#ignoring virtual environment generated folder on ubuntu
venv/
#temp files
Temps/
#test case files
testcases/
```