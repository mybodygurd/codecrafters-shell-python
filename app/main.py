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
            command, *tokens = inp_line.split()
            n_tokens = len(tokens) 
            
            if inp_line == 'exit 0':
                sys.exit()
                
            elif command == 'echo':
                print(' '.join(tokens))
                
            elif command == 'type':
                if not n_tokens:
                    print()
                    continue
                for token in tokens:
                    if token in builtins.keys():
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
                    subprocess.run([path] + tokens)
                    continue
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()
