import sys


def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            if inp_line.startswith('exit 0'):
                sys.exit()
            elif inp_line.startswith('echo '):
                result = inp_line.split('echo ')[0]
                print(result)
            else:    
                print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
