import sys
import os
import subprocess

PATH = os.environ['PATH']
sep = os.pathsep

builtins = {
    "exit": "builtin",
    "echo": "builtin",
    "type": "builtin"
}

def handle_executable_files(command):
    dirs = PATH.split(sep)
    for dir in dirs:
        if os.path.exists(dir):
            try:
                for item in os.listdir(dir):
                    path = os.path.join(dir, item)
                    if '.' in item:
                        item, ext = item.split('.', 1)
                    if os.path.isfile(path) and \
                    (item == command or item + ext == command):                        
                        if os.access(path, os.X_OK):
                            return path
            except(NotADirectoryError, PermissionError):
                raise
    return None
        
    


def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            
            if not inp_line:
                continue
            command, *tokens = inp_line.split()
            n_tokens = len(tokens) == 1
            
            if inp_line == 'exit 0':
                sys.exit()
                
            elif command == 'echo':
                if n_tokens == 0:
                    print()
                    continue
                result = ' '.join(tokens)
                print(result)
                
            elif command == 'type':
                if n_tokens == 1:
                    comm = tokens[0]
                    if comm in builtins.keys():
                        print(f"{comm} is a shell {builtins[comm]}")
                        continue
                    try:
                        path = handle_executable_files(comm)
                    except NotADirectoryError as e:
                        print(f"error in PATH variable directories: {e}")
                        continue
                    except PermissionError:
                        print(f"problem in permission of files")
                        continue
                    if path:
                        print(f"{comm} is {path}")
                    else:
                        print(f"{comm}: not found")
                elif n_tokens == 0:
                    print()
                else:
                    result = ' '.join(tokens)
                    print(f"{result}: not found")
                            
            else:
                path = handle_executable_files(comm)
                if path:
                    result = subprocess.run([comm] + tokens, capture_output=True)
                    print(result)
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
