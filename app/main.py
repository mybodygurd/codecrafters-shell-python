import sys
import os
import subprocess
import shlex
import readline

PATH = os.environ['PATH']
sep = os.pathsep

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
            path = os.path.expanduser('~')
        else:
            path = os.path.expanduser(tokens[0])
        os.chdir(path)

    except FileNotFoundError:
        print(f"{path}: No such file or directory")
    except NotADirectoryError:
        print(f"{path}: Not a Directory")
    except PermissionError:
        print(f"{path}: Permission denied")
    except OSError as e:
        print(f"{path}: OS error({e})")
        
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
    "type": handle_type,
    "pwd": lambda x: print(os.getcwd()),
    "cd": handle_change_dir
}

operators = [">", "1>", ">>", "1>>", "2>", "2>>"]

def redirect(parts):
    for idx in range(len(parts)):
        if parts[idx] in operators:
            cmd_part = parts[: idx]
            file_name = parts[idx + 1]
            if parts[idx] in [">", "1>"]:
                with open(file_name, mode='w') as file:
                    subprocess.run(cmd_part, stdout=file)
            elif parts[idx] in [">>", "1>>"]:
                with open(file_name, mode='a') as file:
                    subprocess.run(cmd_part, stdout=file)
            elif parts[idx] == "2>":
                with open(file_name, mode='w') as file:
                    subprocess.run(cmd_part, stderr=file)
            elif parts[idx] == "2>>":
                with open(file_name, mode='a') as file:
                    subprocess.run(cmd_part, stderr=file)
            return True
    return False

def completer(text, state):
    global last_tab_text, tab_press_count  # You must track these elsewhere

    commands = set(builtins)
    for dir in PATH.split(sep):
        if os.path.isdir(dir):
            try:
                for item in os.listdir(dir):
                    full_path = os.path.join(dir, item)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        commands.add(item)
            except PermissionError:
                continue

    matches = [cmd for cmd in commands if cmd.startswith(text)]

    # Track tab press count for repeated presses
    if state == 0:
        if text == last_tab_text:
            tab_press_count += 1
        else:
            last_tab_text = text
            tab_press_count = 1

        if len(matches) > 1:
            if tab_press_count == 1:
                print('\a', end='', flush=True)
            elif tab_press_count == 2:
                print()  # newline
                print("  ".join(matches))
                print(f"$ {text}", end='', flush=True)

    if state < len(matches):
        return matches[state]
    return None

    

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

            
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
            # if any(op in tokens for op in operators):
            # handled = redirect(parts)
            # if handled:
            #     continue  # ✅ Skip rest of the shell loop (this 'continue' affects the while-loop)
            result = False
            for operator in operators:
                if operator in tokens:
                    result = redirect(parts)
                    if result:
                        break
            if result:
                continue
            if command in builtins:
                handler = builtins[command]
                handler(tokens) 
            else:
                path = handle_executable_files(command)
                if path:
                    subprocess.run([command] + tokens)
                else:    
                    print(f"{inp_line}: command not found")
                
        except KeyboardInterrupt:
            sys.exit(0)
        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    main()
