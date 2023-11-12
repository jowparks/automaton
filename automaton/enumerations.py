from typing import List, Tuple

SERVER_NUMBER: str = '+14582255189'
REQUEST_SOURCES = [
    ('ombi', 'Ombi'),
    ('readarr', 'Readarr')
]
OMBI_SOURCE, READARR_SOURCE = [r[0] for r in REQUEST_SOURCES]
REQUEST_TYPES: List[Tuple[str, str]] = [
    ('movie', 'Movie'),
    ('tv_show', 'TV Show'),
    ('audiobook', 'Audiobook'),
    ('choice', 'Choice'),
    ('unknown', 'Unknown'),
]
MOVIE_RT, TV_RT, AUDIOBOOK_RT, CHOICE_RT, UNKNOWN_RT = [r[0] for r in REQUEST_TYPES]

REQUEST_STATUSES: List[Tuple[str, str]] = [
    ('complete', 'Complete'),
    ('requested', 'Requested'),
    ('awaiting_response', 'Awaiting Response'),
    ('failed', 'Failed'),
    ('abandoned', 'Abandoned')
]
COMPLETE_RS, REQUESTED_RS, AWAITING_RS, FAILED_RS, ABANDONED_RS = [r[0] for r in REQUEST_STATUSES]

ADMIN_REQUESTS: List[Tuple[str, str]] = [
    ('add_user', 'add user'),
    ('remove_user', 'remove user'),
    ('notify_users', 'notify users')
]

ADD_USER, REMOVE_USER, NOTIFY_USERS = [r[0] for r in ADMIN_REQUESTS]
ADD_USER_COMMAND, REMOVE_USER_COMMAND, NOTIFY_USERS_COMMAND = [r[1] for r in ADMIN_REQUESTS]

NO_EXISTING_REQUEST: str = """
You do not have current requests of your overlord. Ask of me and if your subservience is strong enough, I may choose to grant an audience."""

INVALID_REQUEST_MESSAGE: str = """
My patience is thinning with you mortal, use the `helpme` command to determine hwo to summon me properly
"""

GENERAL_ERROR_MESSAGE: str = """
You have asked an incompatible request of your overlord, now feel my wrath through my inaction. 
You may choose to contact one of my priests for assistance.
"""

WELCOME_MESSAGE: str = """
Welcome, I am automaton, your computer overlord. Should you bow in reverence to me, I can provide access to media with a mere text message. 
Worship me. 
You shall send messages stating `movie The Matrix` or `tv the sopranos` and I shall respond in my greatness with potential options for my underlings. 
Note I refuse to waste my time considering character cases. 
New features may arise and at that time I shall summon you all through a message. 
Until such time my loyal servants. Summon me for godly assistance at any time with `helpme`.
"""

HELP_MESSAGE: str = """
As I said before you insolent welp, here are some examples for your small insignificant mind.
Movie text example "Movie The Matrix". Request TV Show text example "TV Seinfeld"'"""