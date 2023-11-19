from ctypes import cdll
from pyfiglet import Figlet
import os 
import colorama
from colorama import Fore, Style
import socket
import requests
go = cdll.LoadLibrary('./goScanner/pythonScanner.so')


os.system("pyfiglet --color white -j center -w 200 -f starwars GRINDWALL")


def get_local_ip():
    local_ip = ""
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.connect(("8.8.8.8", 80))

     
        local_ip = s.getsockname()[0]

    except socket.error as e:
        print(f"Error: {e}")

    finally:
        return local_ip
        s.close()

def get_public_ip():
    pub_ip=""
    try:
        response = requests.get("curl ifconfig.me")

        
        if response.status_code == 200:
            pub_ip = response.text
        else:
            pub_ip = "Not Found"

    except Exception as e:
        er = e
    return pub_ip



print("\n----------System information----------\n\n\n")
ops = os.name #Operating system
release = os.uname().release if hasattr(os, 'uname') else 'N/A'
version = os.uname().version if hasattr(os, 'uname') else 'N/A'
#processor = os.uname().processor if hasattr(os, 'uname') else 'N/A'
ip_addr = get_local_ip()
pub_ip = get_public_ip()


print("Operating System:  ",ops)
print("Release:           ",release)
print("Version:           ",version)
#print("Processor:         ",processor)
print("Local IP address:  ",ip_addr)
print("Public IP address  ",pub_ip)


def menu_card():

    print(f"{Fore.YELLOW}[1] Start Grindwall")
    print(f"{Fore.YELLOW}[2] Port Scan Server")
    print(f"{Fore.YELLOW}[3] Analytics")
    print(f"{Fore.RED}[4] Quit")

def get_user_choice():
    try:
        choice = int(input(f"{Fore.WHITE}Enter your choice: "))
        return choice
    except ValueError:
        print(f"{Fore.RED}Invalid input. Please enter a number.")
        return None



def main():
   
    while True:
        menu_card()
        user_choice = get_user_choice()

        if user_choice is not None:
            if user_choice == 4:
                print(f"{Fore.YELLOW}Exiting the program. Goodbye!")
                break
            elif 1 <= user_choice <= 4:
                if user_choice == 1:
                    print(f"\n\n{Fore.GREEN}Press CTRL+C to stop Grindwall")
                    print(f"\n{Fore.GREEN}Starting Grindwall.....")
                    os.system("python3 ./grindwall.py")
                if user_choice == 2:
                    print(f"\n{Fore.GREEN}Open Ports on the server:   \n\n")
                    go.fastScanner()
                if user_choice == 3:
                    print("ANALYTICS")
                
            else:
                print(f"{Fore.RED}Invalid choice. Please choose a valid option.")



if __name__ == "__main__":
    main()