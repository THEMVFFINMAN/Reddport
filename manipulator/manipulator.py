import random
import requests
import socket
import socks
import subprocess
import time
from utils import ColoredOutput
from fake_useragent import UserAgent

class Manipulator(object):
    """
    """
    def __init__(self, tor_cmd):
        self.user_agent_class = UserAgent(cache=False)
        self.user_agent = self.user_agent_class.random
        self.pretty_print = ColoredOutput()
        self.hdrs = {
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.reddit.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        self.create_payload = {
            'api_type': 'json',
            'passwd2': '',
            'op': 'reg',
            'passwd': '',
            'dest': 'https%3A%2F%2Fwww.reddit.com%2F',
            'user': ''
        }
        self.create_url = 'https://www.reddit.com/api/register/'
        self.login_payload = {
            'op': 'login',
            'api_type': 'json',
            'user': '',
            'passwd': '',
            'dest': 'https%3A%2F%2Fwww.reddit.com%2F'
        }
        self.login_url = 'https://www.reddit.com/api/login/'
        self.report_url = 'https://www.reddit.com/api/report'
        self.tor_cmd = tor_cmd
        self._set_socket()
        self.anonymize()
        self.pretty_print.print_good("Initialized Manipulator successfully")

    def login(cls, username, password):
        """
        Logs in to reddit and creates a requests Session to use for
        follow-up requests via this object
        
        :param str username: username to login with
        :param str password: password to login with
        """
        cls.session = requests.Session()
        cls.login_payload['user'] = username
        cls.login_payload['passwd'] = password
        url = cls.login_url + username
        while True:
            r = cls.session.post(url, headers=cls.hdrs, data=cls.login_payload)
            if r.status_code != 200:
                cls.pretty_print.print_bad("Logging in returned the status code: {}".format(r.status_code))
                continue
            if r.json()['json']['errors']:
                cls.pretty_print.print_bad("Logging in json errorse: {}".format(r.json()['json']['errors']))

            cls.modhash = r.json()['json']['data']['modhash']
            cls.pretty_print.print_good("Logged in successfully")
            return        

    def logout(cls):
        # Destroy the session for the logged in user
        
        cls.modhash = ''
        cls.session = None

    def _change_user_agent(cls):
        cls.user_agent = cls.user_agent_class.random
        cls.pretty_print.print_good("Changed User Agent Successfully")

    def _change_proxy(cls):
        cls.pretty_print.print_good("Initializing Tor")
        subprocess.call(cls.tor_cmd.split(), shell=False)
        cls.pretty_print.print_good("Waiting 5 seconds for Tor to restart")
        time.sleep(5)
        cls.pretty_print.print_good("Changed proxy successfully")

    def anonymize(cls):
        # Clears cookies, changes user agent, restarts Tor (for new IP)
        cls._change_user_agent()
        cls._change_proxy()

    def _set_socket(cls):
        socks.setdefaultproxy(socks.SOCKS5, "127.0.0.1", 9050)
        #patch the socket module
        socket.socket = socks.socksocket
        
        cls.pretty_print.print_good("Set Socket Successfully")

    def report(cls, postid, subreddit, reason):
        payload = {
            'thing_id': postid,
            'reason': "other",
            'other_reason': reason,
            'id': "#report-action-form",
            'r': subreddit,
            'uh': cls.modhash,
            'renderstyle': "html"
        }
        while True:
            r = cls.session.post(cls.report_url, headers=cls.hdrs, data=payload)
            
            if r.status_code != 200:
                continue
            if '"success": true' in r.text:
                cls.pretty_print.print_good("Post: {} Reported successfully".format(postid))
                return
            else:
                raise Exception('Voting failed. Might be the ID')
        

    def test(cls):
        cls.pretty_print.print_good("IP Address: {}".format(requests.get('http://icanhazip.com').text).replace('\n',''))
