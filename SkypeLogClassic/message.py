# This Python file uses the following encoding: utf-8
"""Chats.
"""

import time

MSGTYPE_SETTOPIC = 2
MSGTYPE_CREATEGROUPROOM = 4
MSGTYPE_MEMBER_ADD = 10
MSGTYPE_MEMBER_KICK = 12
MSGTYPE_MEMBER_LEAVE = 13
MSGTYPE_SETROLE = 21
MSGTYPE_CALL_START = 30
MSGTYPE_CALL_END = 39
MSGTYPE_CONTACTINFO_REQ = 50
MSGTYPE_CONTACTINFO_ACK = 51
MSGTYPE_BLOCK = 53
MSGTYPE_ME = 60
MSGTYPE_MSG = 61
MSGTYPE_SENDCONTACT = 63
MSGTYPE_SENDFILE = 68
MSGTYPE_VIDEOMSG = 70
MSGTYPE_BIRTHDAY = 110
MSGTYPE_MEDIA = 201

MSG_TYPES = [MSGTYPE_SETTOPIC, MSGTYPE_CREATEGROUPROOM,
             MSGTYPE_MEMBER_ADD, MSGTYPE_MEMBER_KICK, MSGTYPE_MEMBER_LEAVE,
             MSGTYPE_SETROLE, MSGTYPE_CALL_START, MSGTYPE_CALL_END,
             MSGTYPE_CONTACTINFO_REQ, MSGTYPE_CONTACTINFO_ACK,
             MSGTYPE_BLOCK, MSGTYPE_ME, MSGTYPE_MSG, MSGTYPE_SENDCONTACT,
             MSGTYPE_SENDFILE, MSGTYPE_VIDEOMSG, MSGTYPE_BIRTHDAY,
             MSGTYPE_MEDIA]

CHAT_SPLIT_THRESHOLD = 3600
CHAT_SPLIT_THRESHOLD_WEAK = 3600 * 2
CHAT_SPLIT_THRESHOLD_WEAK_COUNT = 5

class Message:
    def __init__(self, msgtype, chatmsg_type, timestamp, skypeid, dispname,
                 participants, message, message_formatdict, message_body):
        self.msgtype = msgtype
        self.chatmsg_type = chatmsg_type
        
        self.timestamp = timestamp
        self.participants = participants
        
        self.skypeid = skypeid
        self.dispname = dispname
        
        self.message = message
        self.message_formatdict = message_formatdict
        self.message_body = message_body

        self.m = None
    
    def set_m(self, m):
        self.m = m

class Chat:
    def __init__(self, messages=None, skypeid="", dispname=u"", participants=None):
        self.messages = messages if messages else []
        self.skypeid = skypeid
        self.dispname = dispname
        if participants:
            self.participants = list(participants)
        else:
            self.participants = list()

    def set_skypeid(self, skypeid):
        self.skypeid = skypeid

    def set_dispname(self, dispname):
        self.dispname = dispname
    
    def set_participants(self, participants):
        self.participants = participants

    def split(self):
        _splitted = []

        _chat = []
        _last_timestamp = time.mktime(time.localtime())
        _is_call_on_progress = False
        for m in self.messages:
            _interval = time.mktime(m.timestamp) - _last_timestamp
            _last_timestamp = time.mktime(m.timestamp)

            if (_interval > CHAT_SPLIT_THRESHOLD and \
                len(_chat) >= CHAT_SPLIT_THRESHOLD_WEAK_COUNT and \
                not _is_call_on_progress) or \
               (_interval > CHAT_SPLIT_THRESHOLD_WEAK and \
                len(_chat) < CHAT_SPLIT_THRESHOLD_WEAK_COUNT and \
                not _is_call_on_progress):

                _splitted.append(Chat(messages=_chat,
                                skypeid=self.skypeid,
                                dispname=self.dispname,
                                participants=self.participants))
                _chat = []

            if m.msgtype == MSGTYPE_CALL_START:
                _is_call_on_progress = True
            elif m.msgtype == MSGTYPE_CALL_END:
                _is_call_on_progress = False

            _chat.append(m)
        if len(_chat) > 0:
            _splitted.append(Chat(messages=_chat,
                                skypeid=self.skypeid,
                                dispname=self.dispname,
                                participants=self.participants))

        return _splitted
