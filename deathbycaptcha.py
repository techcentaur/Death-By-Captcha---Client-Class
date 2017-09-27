import deathbycaptcha
#declaring the class Client
class Client(object):
    """Death by Captcha API Client"""
    def __init__(self, username, password):
        self.is_verbose = False
        self.userpwd = {'username': username,
                        'password': password}

    def _load_file(self, captcha):
        if hasattr(captcha, 'read'):
            raw_captcha = captcha.read()
        elif type(captcha) == bytearray:
            raw_captcha = captcha
        elif os.path.isfile(captcha):
            raw_captcha = ''
            try:
                f = open(captcha, 'rb')
            except Exception:
                raise e
            else:
                raw_captcha = f.read()
                f.close()
        else:
            f_stream = urllib.urlopen(captcha)
            raw_captcha = f_stream.read()
            
        if not len(raw_captcha):
            raise ValueError('CAPTCHA image is empty')
        elif imghdr.what(None, raw_captcha) is None:
            raise TypeError('Unknown CAPTCHA image type')
        else:
            return raw_captcha

    def _log(self, cmd, msg=''):
        if self.is_verbose:
            print (time.time()+cmd+msg.rstrip())
        return self


    def get_user(self):
        """Fetch the user's details dict -- balance, rate and banned status."""
        raise NotImplemented()

    def get_balance(self):
        """Fetch the user's balance (in US cents)."""
        return self.get_user().get('balance')

    def get_captcha(self, cid):
        """Fetch a CAPTCHA details dict -- its ID, text and correctness."""
        raise NotImplemented()

    def get_text(self, cid):
        """Fetch a CAPTCHA text."""
        return self.get_captcha(cid).get('text') or None

    def report(self, cid):
        """Report a CAPTCHA as incorrectly solved."""
        raise NotImplemented()

    def remove(self, cid):
        """Remove an unsolved CAPTCHA."""
        raise NotImplemented()

    def upload(self, captcha):
        """Upload a CAPTCHA.
        Accepts file names and file-like objects.  Returns CAPTCHA details
        dict on success.
        """
        raise NotImplemented()

    def decode(self, captcha, timeout=DEFAULT_TIMEOUT):
        """Try to solve a CAPTCHA.
        See Client.upload() for arguments details.
        Uploads a CAPTCHA, polls for its status periodically with arbitrary
        timeout (in seconds), returns CAPTCHA details if (correctly) solved.
        """
        deadline = time.time() + (max(0, timeout) or DEFAULT_TIMEOUT)
        c = self.upload(captcha)
        if c:
            while deadline > time.time() and not c.get('text'):
                time.sleep(POLLS_INTERVAL)
                c = self.get_captcha(c['captcha'])
            if c.get('text') and c.get('is_correct'):
                return c



#the main function
if '__main__' == __name__:
    import sys
    #sys.argv[1] will be the DBC account username and sys.argv[2] will be the account password
    client = deathbycaptcha.SocketClient(sys.argv[1], sys.argv[2])
    client.is_verbose = True

    #printing the balance in the DBC account
    print ('Your balance is %s US cents' % client.get_balance())
    try:
        for fn in sys.argv[3:]:
            try:
                #CAPTCHA image file name in sys.argv[3:]
                # DEFAULT TIMEOUT : the timeout
                captcha = client.decode(fn, DEFAULT_TIMEOUT)
            except Exception:
                sys.stderr.write('Failed uploading CAPTCHA: %s\n' % (e, ))
                captcha = None

            if captcha:
                print ('CAPTCHA %d solved: %s' % (captcha['captcha'], captcha['text']))
                try:
                    client.report(captcha['captcha'])
                except Exception:
                    sys.stderr.write('Failed reporting CAPTCHA: %s\n' % (e, ))
    except deathbycaptcha.AccessDeniedException:
        print("AccesDeniedException : Access to DBC API denied, check your credentials and/or balance")

