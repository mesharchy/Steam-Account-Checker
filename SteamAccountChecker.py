from winreg import ConnectRegistry, OpenKey, EnumValue, HKEY_CURRENT_USER
import requests
from bs4 import BeautifulSoup
import os
import time
from colorama import init, Fore, Back, Style


class SteamAccountsChecker:
    def __init__(self, steam_path):
        try:
            self.loginusers = f'{steam_path}/config/loginusers.vdf'
            self.userdata = f'{steam_path}/userdata'

            self.lu_steamids = self.get_login_users()
            print(f' [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] Account detection method #1 works')
            self.ud_steamids = self.get_userdata_ids()
            print(f' [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] Account detection method #2 works')
            self.steamids = self.convert_ids()
            print(f' [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] Account information collected and sorted')
            accounts_list = self.check_steamids()
            if len(accounts_list) > 0:
                print(
                    f'\n' + f' [{Fore.GREEN}Information{Fore.LIGHTWHITE_EX}] Total number of accounts detected: {Fore.LIGHTGREEN_EX}{len(accounts_list)}' + '\n' + '\n'.join(
                        [f'{Fore.LIGHTWHITE_EX}{account}' for account in accounts_list]))
                try:
                    os.remove('accounts.txt')
                except FileNotFoundError:
                    pass
                with open('accounts.txt', 'a', encoding='utf-8') as file:
                    file.write('\n'.join(accounts_list))
                print(
                    f'\n [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] The program has finished analyzing the accounts\n [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] All the accounts have been saved in "accounts.txt"\n [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] Press ENTER to close the program.')
                input()
            else:
                print(f' {Fore.LIGHTRED_EX}[Logging] Steam accounts are not detected on PC')
        except Exception as Error:
            print(f'[{Fore.LIGHTRED_EX}Error{Fore.LIGHTWHITE_EX}]: {Error}')
            time.sleep(0.5)
            SteamAccountsChecker(steam_path=steam_path)

    def get_login_users(self):
        steamids64 = []
        with open(self.loginusers, 'r', encoding='utf-8') as f:
            loginusers_text = f.read()
        loginusers_text = loginusers_text.replace('"', '')
        loginusers_dict = loginusers_text.split()
        for word in loginusers_dict:
            if word.startswith('765'):
                steamids64.append(word)
        return steamids64

    def get_userdata_ids(self):
        userdata_paths = os.listdir(self.userdata)
        steamids64 = []

        def steamid_convert(steamid):
            steamid = f'STEAM_0:0:{steamid}'
            steamid64ident = 76561197960265728
            for ch in ['[', ']']:
                if ch in steamid:
                    steamid = steamid.replace(ch, '')
            steamid_split = steamid.split(':')
            steamid64 = int(steamid_split[2]) + steamid64ident
            return steamid64

        for path in userdata_paths:
            steamids64.append(str(steamid_convert(path)))
        return steamids64

    def convert_ids(self):
        steamids_dirty = self.lu_steamids + self.ud_steamids
        success_steamids = []
        [success_steamids.append(x) for x in steamids_dirty if x not in success_steamids]
        return success_steamids

    def check_steamids(self):
        check_steamids_list = []
        account_index = 1
        for steamid in self.steamids:
            link = f'https://steamcommunity.com/profiles/{steamid}'
            response = requests.get(url=link).text
            soup = BeautifulSoup(response, 'html.parser')
            steam_nickname = soup.find('span', class_='actual_persona_name').text
            try:
                steam_level = soup.find('span', class_='friendPlayerLevelNum').text
            except AttributeError:
                steam_level = 0
            try:
                status = soup.find('div', class_='profile_ban_status').text
                account_bans_status = 'Banned'
            except AttributeError:
                account_bans_status = 'Clean'
            check_steamids_list.append(
                f' • Account #{account_index} » SteamID: {steamid} × Username: {steam_nickname} × Steam Level: {steam_level} × Account Status: {account_bans_status}')
            account_index += 1
        return check_steamids_list


if __name__ == '__main__':
    try:
        os.system('title Steam Account Checker by mesharchy')
        init()
        print(f'\n {Fore.LIGHTWHITE_EX}Welcome to {Fore.LIGHTGREEN_EX}Steam Account Checker')
        print(f' {Fore.LIGHTWHITE_EX}Version: {Fore.GREEN}1.1\n')
        print(
            f' {Fore.LIGHTWHITE_EX}Developer Contact:\n • Telegram: {Fore.GREEN}@mesharchy\n {Fore.LIGHTWHITE_EX}• Discord: {Fore.GREEN}mesharchy#0001\n {Fore.LIGHTWHITE_EX}• GitHub: {Fore.GREEN}https://github.com/mesharchy')
        time.sleep(5)
        os.system('cls')

        aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
        aKey = OpenKey(aReg, r"SOFTWARE\Valve\Steam")
        reg_steam_path = EnumValue(aKey, 2)[1]
        print(f'\n [{Fore.GREEN}Logging{Fore.LIGHTWHITE_EX}] Steam data detected on PC')
        SteamAccountsChecker(steam_path=reg_steam_path)
    except FileNotFoundError:
        print(f'\n {Fore.LIGHTRED_EX}[Error] Steam data not detected on PC')
        time.sleep(10)
        exit()
