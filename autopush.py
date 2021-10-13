import sys
import os
import paramiko
from colorama import init, Fore, Back, Style
from getpass import getpass
import inquirer

beg = Fore.GREEN + "[" + Fore.YELLOW + "*" + Fore.GREEN + "] " + Style.RESET_ALL
beg_safe = Fore.GREEN + "[" + Fore.YELLOW + "+" + Fore.GREEN + "] " + Style.RESET_ALL
beg_error = Fore.RED + "[" + Fore.LIGHTRED_EX + "x" + Fore.RED + "] " + Style.RESET_ALL
beg_input = Fore.RED + "[" + Fore.CYAN + "?" + Fore.RED + "] " + Style.RESET_ALL

ssh_info = {
    "host": "192.168.143.11",
    "port": 22,
    "username": "",
    "password": ""

}

_welcome = """
                           ,     \    /      ,
                          / \    )\__/(     / \\
                         /   \  (_\  /_)   /   \\
            ____ _______/_____\__\@  @/___/_____\___________
            |                    |\../|                    |
            |                     \VV/                     |
            |                BRUNO SSH PUSH                |
            |                author: Joss C                |
            |______________________________________________|
                    |    /\ /      \\\\       \ /\    |
                    |  /   V        ))       V   \  |
                    |/     `       //        '     \|

python3 autopush.py
make sure to be connected to the VPN
"""


class ControllerSSH:
    __ssh = None
    __sftp = None

    # CONNEXION
    @staticmethod
    def connect_client():
        if ControllerSSH.__ssh is None:
            try:
                print(beg + Back.CYAN + Fore.BLACK + "Connexion SSH..." + Style.RESET_ALL)
                ControllerSSH.__ssh = paramiko.Transport((ssh_info['host'], ssh_info['port']))
                ControllerSSH.__ssh.connect(username=ssh_info['username'], password=ssh_info["password"]) 
                return
            except:
                raise ValueError(beg_error + Back.LIGHTRED_EX + "Error connexion ssh..." + Style.RESET_ALL)

    @staticmethod
    def create_sftp_connexion():
        if ControllerSSH.__ssh is None:
            raise ValueError(beg_error + Fore.LIGHTRED_EX + 'You need to connect in ssh before try to connect as sftp'+ Style.RESET_ALL)
        else:
            if ControllerSSH.__sftp is None:
                print(beg + Back.CYAN + Fore.BLACK + "Connexion SFTP..." + Style.RESET_ALL)
                ControllerSSH.__sftp = paramiko.SFTPClient.from_transport(ControllerSSH.__ssh)
                return
        return

    # FILE CONTROLE
    @staticmethod
    def sftp_push_file(path, localfile):
        if ControllerSSH.__sftp is None:
            raise ValueError(beg_error + Fore.LIGHTRED_EX + 'Try to push file before init sftp connexion'+ Style.RESET_ALL)
        ControllerSSH.__sftp.put(localfile, path)
        print(beg + 'the file has been pushed')
        return
    
    @staticmethod
    def sftp_get_file(path, localfile):
        if ControllerSSH.__sftp is None:
            raise ValueError(beg_error + Fore.LIGHTRED_EX + 'Try to get file before init sftp connexion'+ Style.RESET_ALL)
        ControllerSSH.__sftp.get(path, localfile)
        print(beg + 'you can find the file in localpath')
        return

    # DECONNEXION
    @staticmethod
    def disconnect_sftp():
        if ControllerSSH.__sftp:
            print(beg + Back.CYAN + Fore.BLACK + "Deconnexion SFTP..." + Style.RESET_ALL)
            ControllerSSH.__sftp.close()
            ControllerSSH.__sftp = None
            return
    
    @staticmethod
    def disconnect_ssh():
        if ControllerSSH.__ssh:
            print(beg + Back.CYAN + Fore.BLACK + "Deconnexion Session..." + Style.RESET_ALL)
            ControllerSSH.__ssh.close()
            ControllerSSH.__ssh = None
            return

def initPassord():
    global ssh_info
    req = getpass(beg_input + 'Password: ')
    if req == "99":
        return initSSH()
    ssh_info['password'] = req

def initSSH():
    global ssh_info
    req = input(beg_input + 'Username: ')
    if req == "99": 
        return initSSH()
    ssh_info['username'] = req
    initPassord()

def transfertFile():
    print(beg + 'push file')
    questions = [inquirer.List('import',
        message="Do you like to push file or pull file",
        choices=['Push', 'Pull']),
    ]
    answers = inquirer.prompt(questions)
    action = answers["import"]
    if action == 'Push':
        print(beg + 'push file')
        questions = [inquirer.List('td',
            message="Which TD do you want to push in ?",
            choices=['TD1', 'TD2', 'TD3', 'TD4']),
        ]
        answers = inquirer.prompt(questions)
        td = answers["td"]
        localpath = input(beg_input + "Local file (eg: ./index.php): ")
        filename = localpath.split('/')[-1]
        destpath = "/home/"+ssh_info['username']+"/www/A314/"+td+'/'+filename
        print(beg + destpath)
        try:
            pushed = ControllerSSH.sftp_push_file(destpath, localpath)
        except:
            print(beg_error + "Error when pushing the file, make sure your file exist and the path you want to push in is valid")
    else:
        print(beg + 'pull file')
        questions = [inquirer.List('td',
            message="Which TD ?",
            choices=['TD1', 'TD2', 'TD3', 'TD4']),
        ]
        answers = inquirer.prompt(questions)
        td = answers["td"]
        serverFile = input(beg_input + "File name (eg: index.php): ")
        filename = serverFile.split('/')[-1]
        destpath = "/home/"+ssh_info['username']+"/www/A314/"+td+'/'+filename
        print(beg + destpath)
        try:
            pulled = ControllerSSH.sftp_get_file(destpath, './'+filename)
        except:
            print(beg_error + "Error when pulling the file, make sure your file exist and the path you want to push in is valid")
    questions = [inquirer.List('continue',
        message="Other files ?",
        choices=['Yes', 'No']),
    ]
    answers = inquirer.prompt(questions)
    other = answers["continue"]
    if other == "Y" or other == "y" or other == "Yes" or other == "yes":
        return transfertFile()
    else:
        return
        

def main():
    print(_welcome)
    questions = [inquirer.List('install',message="Install requirements ?", choices=['Yes', 'No'])]
    answers = inquirer.prompt(questions)
    install = answers["install"]
    if install == "Yes":
        print(beg + "Installing packages ...")
        os.system("python3 -m pip install paramiko colorama inquirer")
        print(beg + "Pachages installed")
    try:
        initSSH()
        login = ControllerSSH.connect_client()
        sftpin = ControllerSSH.create_sftp_connexion()
    except:
        print(beg_error + "Error: make sure you logins info are right")
        exit()
    transfertFile()
    sftpout = ControllerSSH.disconnect_sftp()
    logout = ControllerSSH.disconnect_ssh() 
    print(beg + 'Good by')

main()
