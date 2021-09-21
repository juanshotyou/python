import base64
from getpass import getpass

def generateAuth():
    username = input("Please input the username:\n")
    password = getpass("Please input the password:\n")
    string2encode = username + ":" + password
    return base64.b64encode(string2encode.encode('UTF-8')).decode('ASCII')

def main():
    token = generateAuth()
    print(f"Your Base64 encoded token is {token}")

if __name__ == "__main__":
    main()