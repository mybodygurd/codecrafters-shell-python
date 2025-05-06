import sys
import os

PATH = os.environ['PATH']
sep = os.pathsep

builtins = {
    "exit": "builtin",
    "echo": "builtin",
    "type": "builtin"
}

def handle_executable_files(command):
    try:
        dirs = PATH.split(sep)
        for dir in dirs:
            if os.path.exists(dir):
                for item in os.listdir(dir):
                    path = os.path.join(dir, item)
                    item = item.split('.')[0]
                    if os.path.isfile(path) and item == command:                        
                        if os.access(path, os.X_OK):
                            return path
        return None
        
    except (NotADirectoryError, PermissionError):
        raise


def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            
            if not inp_line:
                continue
            command, *tokens = inp_line.split()
            
            if command == 'exit 0':
                sys.exit()
                
            elif command == 'echo':
                result = ' '.join(tokens)
                print(result)
                
            elif command == 'type':
                if len(tokens) == 1:
                    comm = tokens[0]
                    path = handle_executable_files(comm)
                    if path:
                        print(f"{comm} is {path}")
                    
                    elif comm in builtins.keys():
                        print(f"{comm} is a shell {builtins[comm]}")
                    else:
                        print(f"{comm}: not found")
                else:
                    result = ' '.join(tokens)
                    print(f"{result}: not found")                

            else:    
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
