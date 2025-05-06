import sys


def main():
    while True:
        try:
            sys.stdout.write("$ ")

            inp_line = input().strip()
            if inp_line:
                print(f"<{inp_line}>: command not found")
                
        except KeyboardInterrupt:
            sys.exit()

if __name__ == "__main__":
    main()
