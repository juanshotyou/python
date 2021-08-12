import os

print(os.getcwd())

newfile = open("newfile.txt", "x")   #Will fail if file already exists

with open("newfile.txt", "a+") as data:
    data.write("\nHere's one line of text...")
    for i in range(9):
        data.write("\nThe index is " + str(i) + "!")
    print("Closing file...")

with open("newfile.txt", "r") as data:
    print(data.read())