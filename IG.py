import json
import pathlib
import threading
from argparse import ArgumentParser

import instaloader

Green = "\033[1;33m"
Blue = "\033[1;34m"
Grey = "\033[1;30m"
Red = "\033[1;31m"
Reset = "\033[0m"

class IG(object):
    class LockedIterator(object):
        def __init__(self, it):
            self.lock = threading.Lock()
            self.it = it.__iter__()

        def __iter__(self):
            return self

        def __next__(self):
            self.lock.acquire()
            try:
                return self.it.__next__()
            finally:
                self.lock.release()
                
    def __init__(self, session, username):

        self.login_profile = str(session)
        self.target_profile = str(username)
        self.fpath = str(pathlib.Path(__file__).parent.absolute())+"/profiles/"
        self.insta = instaloader.Instaloader(quiet=True, max_connection_attempts=1)
        self.insta.load_session_from_file(self.login_profile)
        self.profile = instaloader.Profile.from_username(self.insta.context, self.target_profile)
        self.diff()
        
    def data(self):

        self.new_followees = set()
        self.new_followers = set()
        self.old_followees = set()
        self.old_followers = set()

        def fetch():

            def fetch_followers():
                for name in self.LockedIterator(self.profile.get_followers()):
                    self.new_followers.add(name.username)

            def fetch_followees():
                for name in self.LockedIterator(self.profile.get_followees()):
                    self.new_followees.add(name.username)

            threads = []
            for _ in range(2):
                t = threading.Thread(target=fetch_followers)
                threads.append(t)
                t.start()
            for _ in range(2):
                t = threading.Thread(target=fetch_followees)
                threads.append(t)
                t.start()
            t = threading.Thread(target=read_old)
            threads.append(t)
            t.start()
            for t in threads:
                t.join()

        def read_old():
            if pathlib.Path(self.fpath+self.target_profile+"/following.json").is_file():
                with open(self.fpath+self.target_profile+"/following.json") as user_data: 
                    data = json.load(user_data) 
                self.old_followees = set(data["followees"])
                self.old_followers = set(data["followers"])
            else:
                pass
                
        def write_new():
            pathlib.Path(self.fpath+self.target_profile).mkdir(parents=True,exist_ok=True)
            following = {
                "followers": list(self.new_followers),
                "followees": list(self.new_followees)
                }
            with open(self.fpath+self.target_profile+"/following.json", "w") as user_data:
                json.dump(following, user_data, default=str ,indent=4)

        fetch()
        write_new()
        # return self.new_followers,self.new_followees,self.old_followers,self.old_followees

    def diff(self):
        print(f'\n{Blue}{self.target_profile}:\n{Grey}{"=" * (len(self.target_profile)+1)}{Reset}\n\n')
        self.data()
        print(f'{Green}Followers:  {len(self.new_followers)}{Grey} ({len(self.new_followers) - len(self.old_followers)}){Reset}')
        print(f'followed {self.target_profile}:\t\t\t{Blue}{self.new_followers - self.old_followers}{Reset}')
        print(f'unfollowed {self.target_profile}:\t\t\t{Blue}{self.old_followers - self.new_followers}\n{Reset}')
        print(f'{Green}Following:  {len(self.new_followees)}{Grey} ({len(self.new_followees) - len(self.old_followees)}){Reset}')
        print(f'{self.target_profile} followed:\t\t\t{Blue}{self.new_followees - self.old_followees}{Reset}')
        print(f'{self.target_profile} unfollowed:\t\t\t{Blue}{self.old_followees - self.new_followees}\n\n{Reset}')
        print(f'{Grey}{"=" * (len(self.target_profile)+1)}{Reset}\n')


# def args():
#     args = ArgumentParser()
#     args.add_argument('session', help='username of login session')
#     args.add_argument('username', help='target email or username')
#     return args.parse_args()