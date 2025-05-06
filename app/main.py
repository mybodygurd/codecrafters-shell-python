import sys

builtins = {
    "exit": "builtin",
    "echo": "builtin",
    "type": "builtin"
}


def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            if inp_line.startswith('exit 0'):
                sys.exit()
            elif inp_line.startswith('echo '):
                result = inp_line.split('echo ')[1]
                print(result)
            elif inp_line.startswith('type '):
                result = inp_line.split('type ')[1].split()[0]
                if result in builtins.keys():
                    print(f"{result} is a shell {builtins[result]}")
                else:
                    print(f"{result}: not found")                

            else:    
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
