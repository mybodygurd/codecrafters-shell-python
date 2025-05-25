import sys
import os
import subprocess
import shlex
import readline
import io

PATH = os.environ['PATH']
sep = os.pathsep

last_tab_text = ""
tab_press_count = 0
HISTORY = []

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

def add_history(line: str) -> None:
    HISTORY.append(line)
    
def handle_history(tokens: list[str]):
    for line in HISTORY:
        print(line)
    
    

builtins = {
    "exit": handle_exit,
    "echo": lambda x: print(' '.join(x)),
    "type": handle_type,
    "pwd": lambda x: print(os.getcwd()),
    "cd": handle_change_dir,
    "history": handle_history
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
    global last_tab_text, tab_press_count

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

    matches = [cmd for cmd in sorted(commands) if cmd.startswith(text)]

    # Track how many times <TAB> was pressed on the same input
    if state == 0:
        if text == last_tab_text:
            tab_press_count += 1
        else:
            last_tab_text = text
            tab_press_count = 1

        # On first tab, ring bell if multiple matches
        if len(matches) > 1 and tab_press_count == 1:
            print('\a', end='', flush=True)
        # On second tab, print all matches separated by 2 spaces
        elif len(matches) > 1 and tab_press_count == 2:
            print()  # newline
            print("  ".join(matches))  # use two spaces between
            sys.stdout.write(f"$ {text}")
            sys.stdout.flush()

    # When actually returning match (used by readline), add trailing space
    if state < len(matches):
        return matches[state] + ' '
    return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def execute_pipelines(commands):
    n_pipes = len(commands) - 1
    pipes = [os.pipe() for _ in range(n_pipes)]

    for i, cmd in enumerate(commands):
        builtin = cmd[0] in builtins
        pid = os.fork()
        if pid == 0:  # Child process
            # Set up input: Read from previous pipe (not for first command)
            if i > 0:
                os.dup2(pipes[i-1][0], sys.stdin.fileno())
                os.close(pipes[i-1][0])  # Close read end after use
                os.close(pipes[i-1][1])  # Close write end

            # Set up output: Write to next pipe (not for last command)
            if i < n_pipes:
                os.dup2(pipes[i][1], sys.stdout.fileno())
                os.close(pipes[i][0])  # Close read end
                os.close(pipes[i][1])  # Close write end after use

            # Close remaining pipe ends from other pipes
            for j in range(n_pipes):
                if j != i and j != i-1:
                    os.close(pipes[j][0])
                    os.close(pipes[j][1])

            # Execute the command
            if builtin:
                output = io.StringIO()
                sys.stdout = output
                try:
                    builtins[cmd[0]](cmd[1:])
                except Exception as e:
                    print(f"Error in {cmd[0]}: {e}", file=sys.stderr)
                sys.stdout = sys.__stdout__
                print(output.getvalue(), end='')
                output.close()
            else:
                try:
                    subprocess.run(cmd, check=True)
                except subprocess.CalledProcessError as e:
                    print("NIL")
                except FileNotFoundError:
                    print(f"{cmd[0]}: command not found", file=sys.stderr)
                except PermissionError:
                    print(f"{cmd[0]}: permission denied", file=sys.stderr)
            sys.exit(0)
    for pipe in pipes:
        os.close(pipe[0])
        os.close(pipe[1])
    for _ in commands:
        os.wait()
            
def main():
    while True:
        try:
            sys.stdout.write("$ ")
            inp_line = input().strip()
            
            if not inp_line:
                continue
            add_history(inp_line)
            
            pipeline_parts = [part.strip().split() for part in inp_line.split('|')]
            
            if len(pipeline_parts) > 1:
                execute_pipelines(pipeline_parts)
                continue
            parts = shlex.split(inp_line)
            command = parts[0]
            tokens = parts[1:]
            if any(op in tokens for op in operators):
                redirect(parts)
                continue
                
            if command in builtins:
                builtins[command](tokens)
            else:
                path = handle_executable_files(command)
                if path:
                    subprocess.run([command] + tokens)
                else:    
                    print(f"{inp_line}: command not found")      
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

if __name__ == "__main__":
    main()
