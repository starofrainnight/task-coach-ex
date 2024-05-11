# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/> or <http://www.gnu.org/licenses/lgpl.txt>.

import ntlm

class IMAPNtlmAuthHandler(object):
    """Example use:
    
    >>> import imaplib
    >>> imap = imaplib.IMAP_4("my.imap.server")
    >>> imap.authenticate("NTLM", IMAPNtlmAuthHandler(r"DOMAIN\user", "password"))
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.phase = 0
        
    def __call__(self, response):
        if self.phase == 0:
            self.phase = 1
            return ntlm.create_NTLM_NEGOTIATE_MESSAGE(self.username)
        else:
            assert self.phase == 1
            self.phase = 2 # ... finished
            challenge, flags = ntlm.parse_NTLM_CHALLENGE_MESSAGE(response)
            user_parts = self.username.split("\\", 1)
            return ntlm.create_NTLM_AUTHENTICATE_MESSAGE(challenge, user_parts[1], user_parts[0], self.password, flags)