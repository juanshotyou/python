from datetime import datetime
import os

#Print time and location information for the script

runtime = datetime.now()
runtime_str = runtime.strftime("%d-%b-%Y-%H:%M:%S.%f")
print(f"This script was run at {runtime_str} from " + os.getcwd() + ".\n")

#Create a file where you can log all operations of the script

x = 0

while True:
    try:
        filename = input("What name would you like the log file to have? :") 
        with open(filename, "x") as data:
            print(f"Successfully created log file named \"{filename}\"!")
    except FileExistsError:
        print("The name chosen for the log file is already in use. Please choose a different name.")
    else:
        x = 0
        break
    finally:
        x += 1
        if x == 3:
            print("You have entered an invalid filename 3 times.\nCheck the working folder and rerun.")
            break
    
