import sys
import os
import subprocess
import shlex

DIR_SEP = os.sep
HOME_DIR = os.path.expanduser('~')
PATH = os.environ['PATH']
sep = os.pathsep

# def quote_delimiter_checker(string):
#     stack = []
#     for char in string:
#         if char == "'" and "'" not in stack:
#             stack.append("'")
#         elif char == "'" and "'" in stack:
#             stack.pop()
#     return not stack

def handle_executable_files(command):
    dirs = PATH.split(sep)
    for dir in dirs:
        if os.path.exists(dir):
            try:
                for item in os.listdir(dir):
                    path = os.path.join(dir, item)
                    if '.' in item:
                        item, ext = item.split('.', 1)
                    else:
                        ext = ''
                    if os.path.isfile(path) and item.lower() == command.lower():                        
                        if os.access(path, os.X_OK):
                            return path
            except(NotADirectoryError, PermissionError, FileNotFoundError):
                continue
    return None

def handle_change_dir(tokens):
    try:
        if not tokens:
            os.chdir(HOME_DIR)
            
        elif DIR_SEP in tokens:
            dirs = tokens[0].split(DIR_SEP)
            for dir in dirs:
                if dir == '~':
                    os.chdir(HOME_DIR)
                    
                elif dir == '..':
                    current_dir = os.getcwd
                    parent_dir = os.path.dirname(current_dir)
                    os.chdir(parent_dir)
                    
                elif dir == '.':
                    continue
                else:
                    os.chdir(dir)
                    
        elif tokens[0] == '~':
            os.chdir(HOME_DIR)
            
        else:
            path = tokens[0].strip()
            os.chdir(path)
            
    except FileNotFoundError:
        print(f"{path}: No such file or directory")
        raise
    except NotADirectoryError:
        print(f"{path}: is not a directory")
        raise
    except PermissionError:
        print(f"{path}: access denied")
        raise
    except OSError:
        raise
    
def handle_exit(tokens: list):
    exit_code = 0
    try:
        exit_code = int(tokens[0])
    except ValueError:
        sys.stderr.write("exit: numeric argument required\n")
        exit_code = 1
    sys.exit(exit_code)

def handle_type(tokens: list):
    for token in tokens:
        if token in builtins:
            print(f"{token} is a shell builtin")
        else:    
            path = handle_executable_files(token)
            if path:
                print(f"{token} is {path}")
            else:
                print(f"{token}: not found")
 

builtins = {
    "exit": handle_exit,
    "echo": lambda x: print(' '.join(x)),
    "type": "builtin",
    "pwd": lambda x: print(os.getcwd()),
    "cd": handle_change_dir
}
    
        
def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            
            if not inp_line:
                continue
            
            parts = shlex.split(inp_line)
            command = parts[0]
            tokens = parts[1:]
            
            if command in builtins:
                function = builtins[command]
                function(tokens)
                
            else:
                path = handle_executable_files(command)
                if path:
                    subprocess.run([command] + tokens)
                    continue
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit(0)
        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    main()
