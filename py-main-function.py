from datetime import datetime
import os

def print_time_and_cwd():
    runtime = datetime.now()
    runtime_str = runtime.strftime("%d-%b-%Y-%H:%M:%S.%f")
    print(f"This script was run at {runtime_str} from " + os.getcwd() + ".\n")

def create_log_file():
    x = 0
    while True:
        try:
            filename = input("What name would you like the log file to have? :") 
            with open(filename, "x") as data:
                print(f"Successfully created log file named \"{filename}\"!")
        except FileExistsError:
            print("The name chosen for the log file is already in use. Please choose a different name.\n")
        else:
            x = 0
            break
        finally:
            x += 1
            if x == 3:
                print("You have entered an invalid filename 3 times.\nCheck the working folder and rerun.")
                break
    return (filename)

def main():
    print("Hello from the main function!")
    print_time_and_cwd()
    if input("Type 'LOG' if you would like to log the actions of this script to a file: ") == "LOG":
        log_file = create_log_file()
    else: 
        print("This script will continue without logging.")

if __name__ == "__main__":
    main()