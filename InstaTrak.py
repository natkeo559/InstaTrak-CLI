import inquirer
import pathlib
from inquirer.themes import Default
import IG
import os
import sys
import re

Green = "\033[1;33m"
Blue = "\033[1;34m"
Grey = "\033[1;30m"
Red = "\033[1;31m"
Reset = "\033[0m"

c = {0: f'{Red}Target Scan', 1: f'{Red}Settings', 2: f'{Grey}Quit'}


class Insta_CLI:
    def __init__(self) -> None:
        self.main_menu()

    def validate(self, s, remove_session=False):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        if remove_session:
            return ansi_escape.sub('', s)[8:]
        else:
            return ansi_escape.sub('', s)

    def header(self):
        os.system("clear")
        h = f'''{Grey}
            ==================================={Red}
            ░█░█▄░█░▄▀▀░▀█▀▒▄▀▄░▀█▀▒█▀▄▒▄▀▄░█▄▀
            ░█░█▒▀█▒▄██░▒█▒░█▀█░▒█▒░█▀▄░█▀█░█▒█{Grey}
            ==================================={Reset}
            '''
        print(f'{h}')

    def main_menu(self):
        while True:
            main_questions = [
                inquirer.List('option',
                            message=f"Please select an option:{Grey}",
                            choices=list(c.values()),
                            ), ]
            self.header()
            main_menu = inquirer.prompt(main_questions, theme=Default())
            o = main_menu['option']
            if o == c[0]:
                self.target_menu_sessions()
            if o == c[1]:
                self.settings_menu()
            if o == c[2]:
                exit()

    def settings_menu(self):
        c = {0: f'{Red}Setting 1', 1: f'{Red}Setting 2', -1: f'{Grey}Back'}
        settings_questions = [
            inquirer.List('option',
                          message=f"Please select a target:{Grey}",
                          choices=list(c.values()),
                          ), ]
        while True:
            self.header()
            settings = inquirer.prompt(settings_questions, theme=Default())
            break  # select options for settings

    def target_menu_sessions(self):
        avs = {f'{Red}{i}' for i in os.listdir(os.path.expanduser("~/.config/instaloader/"))}
        c = {**dict(enumerate(avs)), **{-1: f'{Red}New Session', -2: f'{Grey}Back'}}

        session_questions = [
            inquirer.List('option',
                          message=f"Please select a session:{Grey}",
                          choices=list(c.values()),
                          ), ]

        session_names = [
            inquirer.Text('session_name',
                          message='Session username'),
            inquirer.Password('session_pass',
                              message='Session password')
        ]
        while True:
            self.header()
            session = inquirer.prompt(session_questions, theme=Default())
            if session['option'] == c[-2]:
                self.main_menu()
            # Make a new session
            elif session['option'] == c[-1]:
                self.header()
                session_login = inquirer.prompt(session_names, theme=Default())
                # store new session then go back to session selection
            else:
                self.target_menu_user(self.validate(
                    session['option'], remove_session=True))

    def target_menu_user(self, session):
        avs = [f'{Red}{i}' for i in os.listdir(str(pathlib.Path(__file__).parent.absolute())+"/profiles/") if i != '.DS_Store']
        c = {**dict(enumerate(avs)), **{-1: f'{Red}New Target', -2: f'{Grey}Back'}}
        target_questions = [
            inquirer.List('option',
                          message=f"Please select a target:{Grey}",
                          choices=list(c.values()),
                          ), ]

        target_names = [
            inquirer.Text('target_name',
                          message='Target username')]

        while True:
            self.header()
            target = inquirer.prompt(target_questions, theme=Default())
            if target['option'] == c[-2]:  # back
                self.target_menu_sessions()

            elif target['option'] == c[-1]:  # New Target
                self.header()
                target_prompt = inquirer.prompt(target_names, theme=Default())
                self.target_search(target_prompt['target_name'], session)

            else:  # Existing Target
                self.target_search(self.validate(target['option']), session)

    def target_search(self, user, session):
        c = {1: f'{Red}Yes', 2: f'{Grey}No (Quit)'}
        complete = [
            inquirer.List('yesno', message='Return to main menu?',
                          choices=c.values())
        ]
        self.header()
        IG.IG(session, user)
        print()
        prompt = inquirer.prompt(complete, theme=Default())
        if prompt['yesno'] == c[1]:
            self.main_menu()
        else:
            exit()


if __name__ == "__main__":
    Insta_CLI()
