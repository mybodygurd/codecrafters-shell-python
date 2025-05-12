import sys
import os
import subprocess
import shlex

DIR_SEP = os.sep
HOME_DIR = os.path.expanduser('~')
PATH = os.environ['PATH']
sep = os.pathsep

builtins = {
    "exit": "builtin",
    "echo": "builtin",
    "type": "builtin",
    "pwd": "builtin"
}

def quote_delimiter_checker(string):
    stack = []
    for char in string:
        if char == "'" and "'" not in stack:
            stack.append("'")
        elif char == "'" and "'" in stack:
            stack.pop()
    return not stack

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
            n_tokens = len(tokens) - 1
            
            if command == 'exit':
                exit_code = 0
                try:
                    exit_code = int(tokens[0])
                except ValueError:
                    sys.stderr.write("exit: numeric argument required\n")
                    exit_code = 1
                sys.exit(exit_code)
                
            elif command == 'echo':
                print(' '.join(tokens))
                
            elif command == 'pwd':
                print(os.getcwd())
                
            elif command == 'cd':
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
                    continue
                except NotADirectoryError:
                    print(f"{path}: is not a directory")
                    continue
                except PermissionError:
                    print(f"{path}: access denied")
                    continue
                except OSError:
                    continue
                
            elif command == 'type':
                print("1 con")
                if not tokens:
                    print("2 con")
                    continue
                for token in tokens:
                    print("3 con")
                    if token in builtins:
                        print(f"{token} is a shell {builtins[token]}")
                    else:    
                        path = handle_executable_files(token)
                        if path:
                            print(f"{token} is {path}")
                        else:
                            print(f"{token}: not found")
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
