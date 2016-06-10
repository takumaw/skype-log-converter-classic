# This Python file uses the following encoding: utf-8
"""Reader.
"""

from . import message

import sys
import logging
import pprint
import base64
import re
import time
import xml.etree.ElementTree
import sqlite3

logger = logging.getLogger(__name__)

class Reader:
    def __init__(self):
        self.conn = None
        
        self._id_to_dispname_table = {}
        self._id_to_dispname_table_cached = {}
        self._m_to_participants_table_cached = {}
    
        self._pp_ = pprint.PrettyPrinter(indent=4, stream=sys.stderr)

    def set_nametable(self, table):
        self._id_to_dispname_table = table

    def load(self, db_filename):
        self.conn = sqlite3.connect(db_filename)
        self.conn.row_factory = sqlite3.Row

    def read(self):
        # read
        account_entries = self.conn.execute("SELECT * FROM Accounts")
        multiple_entries = False
        for r in account_entries:
            if multiple_entries:
                raise RuntimeError('Multiple account found')
            my_skypeid = r["skypename"]
            my_dispname = self._id_to_dispname(my_skypeid)
            self._id_to_dispname_table_cached[my_skypeid] = my_dispname
            multiple_entries = True

        chats = {}
        for m in self.conn.execute("SELECT * FROM Messages ORDER BY timestamp"):
            # type
            _type = m["type"]
            _chatmsg_type = m["chatmsg_type"]
            if _type not in message.MSG_TYPES:
                # UNCAUGHT MESSAGE; FIX THIS
                # raise RuntimeError('Invalid message type: %s' % (m["type"],))
                logger.error('Invalid message type: %s' % (m["type"],))
                self.debug_print_m(m)
                continue
                
            # timestamp
            try:
                _timestamp = time.localtime(m["timestamp"])
            except:
                # UNCAUGHT MESSAGE; FIX THIS
                # raise RuntimeError('Invalid timestamp: %s' % (m["timestamp"],))
                logger.error('Invalid message type: %s' % (m["type"],))
                self.debug_print_m(m)
                continue

            # participants
            __participants = self._m_to_participants(m, my_skypeid)
            if __participants == None:
                # UNCAUGHT MESSAGE; FIX THIS
                # raise RuntimeError('Invalid participants')
                logger.error('Invalid participants')
                self.debug_print_m(m)
                continue
            _participants = []
            for __p in __participants:
                _p_skypeid = __p
                _p_dispname = self._id_to_dispname(__p)
                _p = {'skypeid': _p_skypeid, 'dispname': _p_dispname}
                _participants.append(_p)
            if not _participants:
                logger.error('None participants')
                self.debug_print_m(m)

            # identities
            __identities = m["identities"]
            _identities = None
            if __identities != None:
                _identities = []
                __identities = __identities.split()
                for __i in __identities:
                    _i_skypeid = __i
                    _i_dispname = self._id_to_dispname(__i)
                    _i = {'skypeid': _i_skypeid, 'dispname': _i_dispname}
                    _identities.append(_i)
                _identities_dispname = u", ".join([p['dispname'] for p in _identities])
            else:
                if _type in [message.MSGTYPE_MEMBER_ADD, message.MSGTYPE_MEMBER_KICK,
                            message.MSGTYPE_SETROLE, message.MSGTYPE_CONTACTINFO_ACK]:
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid identities')
                    logger.error('Invalid identities')
                    self.debug_print_m(m)
                    continue
            
            # author
            _skypeid = m["author"]
            #_dispname = m["from_dispname"]
            if not _skypeid:
                # USE THE FIRST PATICIPANTS AS AN AUTHOR
                _skypeid = _identities[0]["skypeid"]
                _dispname = _identities[0]["dispname"]
            else:
                _dispname = self._id_to_dispname(_skypeid)
            
                # UNCAUGHT MESSAGE; FIX THIS
                # raise RuntimeError('Invalid skypeid: %s' % (m["author"],))
                #logger.error('Invalid skypeid: %s' % (m["author"],))
                #self.debug_print_m(m)
                #continue
            
            # key
            _key = " ".join(__participants)
            
            # body_xml
            if m["body_xml"] != None:
                try:
                    _body_xml = self._body_xml_normalize(m["body_xml"])
                    _body_xml_tree = xml.etree.ElementTree.fromstring(_body_xml.encode("utf-8"))
                except:
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid body_xml: %s' % (m["body_xml"],))
                    logger.error('Invalid body_xml: %s' % (m["body_xml"],))
                    self.debug_print_m(m)
                    continue
            else:
                _body_xml = self._body_xml_normalize(u"")
                _body_xml_tree = xml.etree.ElementTree.fromstring(_body_xml.encode("utf-8"))

            # message, message_body
            _message = None
            _message_formatdict = None
            _message_body = None

            if _type == message.MSGTYPE_SETTOPIC:
                _body_xml_cleaned = self._body_xml_tree_enflat(_body_xml_tree)
                # set topic
                if _chatmsg_type == 5:
                    _message = u'%(author)s set topic to "%(topic)s"'
                    _message_formatdict = {'author': _dispname, 'topic': _body_xml_cleaned}
                elif _chatmsg_type == 15:
                    _message = u'%(author)s updated the group picture'
                    _message_formatdict = {'author': _dispname}
                else:
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid _chatmsg_type of message.MSGTYPE_SETTOPIC: %s' % (m["_chatmsg_type"],))
                    logger.error('Invalid _chatmsg_type of message.MSGTYPE_SETTOPIC: %s' % (m["_chatmsg_type"],))
                    self.debug_print_m(m)
                    continue
            elif _type == message.MSGTYPE_CREATEGROUPROOM:
                # invoke a new group room (from this window)
                _message = u'%(author)s created a group conversation'
                _message_formatdict = {'author': _dispname}
            elif _type == message.MSGTYPE_MEMBER_ADD:
                # add new member(s)
                _message = u'%(author)s added %(identities)s to this conversation'
                _message_formatdict = {'author': _dispname, 'identities': _identities_dispname}
            elif _type == message.MSGTYPE_MEMBER_KICK:
                # kick a member
                _message = u'%(author)s has ejected %(identities)s from this conversation'
                _message_formatdict = {'author': _dispname, 'identities': _identities_dispname}
            elif _type == message.MSGTYPE_MEMBER_LEAVE:
                # a member has left
                _message = u'%(author)s has left the conversation'
                _message_formatdict = {'author': _dispname}
            elif _type == message.MSGTYPE_SETROLE:
                # set role
                if m["param_value"] == 5:
                    _role = u"Spectator"
                elif m["param_value"] == 3:
                    _role = u"Speaker"
                elif m["param_value"] == 2:
                    _role = u"Administrator"
                else:
                    _role = u"Unknown" # FIX THIS
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid param_value of message.MSGTYPE_SETROLE: %s' % (m["param_value"],))
                    logger.error('Invalid param_value of message.MSGTYPE_SETROLE: %s' % (m["param_value"],))
                    self.debug_print_m(m)
                
                _message = u'%(author)s set rank of %(identities)s to %(role)s'
                _message_formatdict = {'author': _dispname, 'identities': _identities_dispname, 'role': _role}
            elif _type == message.MSGTYPE_CALL_START or \
                _type == message.MSGTYPE_CALL_END:
                # start call / end call
                if not m["reason"]:
                    _reason = None
                elif m["reason"] == "busy":
                    _reason = u"Busy"
                elif m["reason"] == "no_answer":
                    _reason = u"No answer"
                elif m["reason"] == "manual":
                    _reason = u"No answer"
                elif m["reason"] == "connection_dropped":
                    _reason = u"Connection dropped"
                elif m["reason"] == "unable_to_connect":
                    _reason = u"Unable to connect"
                elif m["reason"] == "internal_error":
                    _reason = u"Internal Error"
                elif m["reason"] == "insufficient_funds":
                    _reason = u"Insufficient Funds"
                else:
                    _reason = u"Unknown" # FIX THIS
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid reason of message.MSGTYPE_CALL_*: %s' % (m["reason"],))
                    logger.error('Invalid reason of message.MSGTYPE_CALL_*: %s' % (m["reason"],))
                    self.debug_print_m(m)
                
                if _type == message.MSGTYPE_CALL_START:
                    # call start
                    if _dispname:
                        _message = u'Call started by %(author)s'
                        _message_formatdict = {'author': _dispname}
                    else:
                        _message = u'Call started'
                elif _type == message.MSGTYPE_CALL_END:
                    if _reason == None:
                        _message = u'Call ended'
                    else:
                        _message = u'Call ended - %(reason)s'
                        _message_formatdict = {'reason': _reason}
            elif _type == message.MSGTYPE_CONTACTINFO_REQ:
                # require contact info
                _message = u'Contact request'
                _message_body = self._body_xml_tree_enflat(_body_xml_tree)
            elif _type == message.MSGTYPE_CONTACTINFO_ACK:
                # share contact info
                _message = u'%(author)s has shared contact details with %(identities)s.'
                _message_formatdict = {'author': _dispname, 'identities': _identities_dispname}
            elif _type == message.MSGTYPE_BLOCK:
                # block a member
                _message = u'Blocked contact'
            elif _type == message.MSGTYPE_ME:
                # Skype command /me ...
                _message_body = self._body_xml_tree_enflat(_body_xml_tree)
            elif _type == message.MSGTYPE_MSG:
                # message
                _message_body = self._body_xml_tree_enflat(_body_xml_tree)
            elif _type == message.MSGTYPE_SENDCONTACT:
                # send contact(s)
                _message = u'%(author)s sent you contact(s)'
                _message_formatdict = {'author': _dispname}
                try:
                    _contacts_to_be_sent = []
                    _contacts = _body_xml_tree.findall(".//c")
                    for _c in _contacts:
                        _contacts_to_be_sent.append(u'<li>' + _c.attrib["f"] + u' (' + _c.attrib["s"] + u')' + u'</li>')
                    _message_body = u'<ul>' + (u''.join(_contacts_to_be_sent)) + u'</ul>'
                except:
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid contact list of message.MSGTYPE_SHARECONTACT')
                    logger.error('Invalid contact list of message.MSGTYPE_SHARECONTACT')
                    self.debug_print_m(m)
                    _message_body = u''
            elif _type == message.MSGTYPE_SENDFILE:
                # send file(s)
                _message = u'%(author)s sent you file(s)'
                _message_formatdict = {'author': _dispname}
                try:
                    _files_to_be_sent = []
                    _files = _body_xml_tree.findall(".//file")
                    for _f in _files:
                        _files_to_be_sent.append(u'<li>' + _f.text + u'</li>')
                    _message_body = u'<ul>' + (u''.join(_files_to_be_sent)) + u'</ul>'
                except:
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid file list of message.MSGTYPE_SENDFILE')
                    logger.error('Invalid file list of message.MSGTYPE_SENDFILE')
                    self.debug_print_m(m)
                    _message_body = u''
            elif _type == message.MSGTYPE_VIDEOMSG:
                # video message
                _message = u'%(author)s sent you a video message'
                _message_formatdict = {'author': _dispname}
            elif _type == message.MSGTYPE_BIRTHDAY:
                # birthday
                _birthday = self._m_id_to_birthday(m, _skypeid)
                _message = u"It's %(author)s's birthday on %(date)s"
                _message_formatdict = {'author': _dispname, 'date': _birthday}
            elif _type == message.MSGTYPE_MEDIA:
                # send media(s)
                _message = u'%(author)s sent you file(s)'
                _message_formatdict = {'author': _dispname}
                try:
                    _text_node = _body_xml_tree.findall(".//Text")[0]
                    _message_body = xml.etree.ElementTree.tostring(_text_node, encoding="utf-8", method="xml")
                    _message_body = _message_body[len("<Text>"):-len("</Text>")].decode("utf-8")
                except Exception as err:
                    print err
                    # UNCAUGHT MESSAGE; FIX THIS
                    # raise RuntimeError('Invalid file list of message.MSGTYPE_SENDFILE')
                    logger.error('Invalid message of message.MSGTYPE_MEDIA')
                    self.debug_print_m(m)
                    _message_body = u''

            # msg
            msg = message.Message(msgtype=_type, chatmsg_type=_chatmsg_type, timestamp=_timestamp,
                skypeid=_skypeid, dispname=_dispname, participants=_participants,
                message=_message, message_formatdict=_message_formatdict, message_body=_message_body)

            # append to chats
            if not chats.has_key(_key):
                chats[_key] = message.Chat(skypeid=my_skypeid,
                                   dispname=my_dispname,
                                   participants=_participants)
            chats[_key].messages.append(msg)

        chats_splitted = []
        for k in chats:
            chats_splitted += chats[k].split()
        return chats_splitted

    def _id_to_dispname(self, skypeid):
        # lookup cache
        if self._id_to_dispname_table.has_key(skypeid):
            self._id_to_dispname_table_cached[skypeid] = self._id_to_dispname_table[skypeid]
            return self._id_to_dispname_table[skypeid]
        elif self._id_to_dispname_table_cached.has_key(skypeid):
            return self._id_to_dispname_table_cached[skypeid]
    
        # search
        try:
            r = self.conn.execute("SELECT * FROM Accounts WHERE skypename=?", (skypeid,)).fetchone()
            fullname = r["fullname"]
            self._id_to_dispname_table_cached[skypeid] = fullname
            return fullname
        except:
            pass
        try:
            rows = self.conn.execute("SELECT * FROM Contacts WHERE skypename=?", (skypeid,))
            r = rows.fetchone()
            fullname = r["fullname"]
            displayname = r["displayname"]
            if fullname != None:
                self._id_to_dispname_table_cached[skypeid] = fullname
                return fullname
            elif displayname != None:
                self._id_to_dispname_table_cached[skypeid] = displayname
                return displayname
            else:
                raise
        except:
            pass
        try:
            rows = self.conn.execute("SELECT * FROM Conversations WHERE identity=?", (skypeid,))
            r = rows.fetchone()
            displayname = r["displayname"]
            self._id_to_dispname_table_cached[skypeid] = displayname
            return displayname
        except:
            pass
        try:
            rows = self.conn.execute("SELECT * FROM Messages WHERE author=? AND from_dispname IS NOT NULL ORDER BY timestamp DESC", (skypeid,))
            r = rows.fetchone()
            from_dispname = r["from_dispname"]
            self._id_to_dispname_table_cached[skypeid] = from_dispname
            return from_dispname
        except:
            pass
        try:
            rows = self.conn.execute("SELECT * FROM Chats WHERE dialog_partner=? AND friendlyname IS NOT NULL", (skypeid,))
            for r in rows:
                if r["friendlyname"].count("|") == 0:
                    self._id_to_dispname_table_cached[skypeid] = r["friendlyname"]
                    return r["friendlyname"]
            # BUGS WHEN NAME HAS "|"
            #for r in rows:
            #    if r["friendlyname"].count("|") >= 1:
            #        friendlyname = r["friendlyname"].split(" | ")[0]
            #        self._id_to_dispname_table_cached[skypeid] = friendlyname
            #        return friendlyname
        except:
            pass
        dispname = unicode(skypeid)
        self._id_to_dispname_table_cached[skypeid] = dispname
        return dispname

    def _m_to_participants(self, m, myid):
        # lookup cache
        if m["convo_id"] and self._m_to_participants_table_cached.has_key(m["convo_id"]):
            return self._m_to_participants_table_cached[m["convo_id"]]
        elif m["chatname"] and self._m_to_participants_table_cached.has_key(m["chatname"]):
            return self._m_to_participants_table_cached[m["chatname"]]
        
        # search
        try:
            participants = []
            rows = self.conn.execute("SELECT * FROM Participants WHERE convo_id=?", (m["convo_id"],))
            r = rows.fetchone()
            _participants = r["identity"].split()
            participants += _participants
        except:
            pass
        try:
            if not m["convo_id"]:
                raise Exception
            rows = self.conn.execute("SELECT * FROM Chats WHERE conv_dbid=? and dialog_partner IS NOT NULL and dialog_partner!=?", (m["convo_id"],myid))
            r = rows.fetchone()
            _participants = r["dialog_partner"].split()
            participants += _participants
        except:
            pass
        try:
            if not m["chatname"]:
                raise Exception
            rows = self.conn.execute("SELECT * FROM Chats WHERE name=? and dialog_partner IS NOT NULL and dialog_partner!=?", (m["chatname"],myid))
            r = rows.fetchone()
            _participants = r["dialog_partner"].split()
            participants += _participants
        except:
            pass
        try:
            if not m["convo_id"]:
                raise Exception
            rows = self.conn.execute("SELECT * FROM Chats WHERE conv_dbid=? and participants IS NOT NULL and participants!=?", (m["convo_id"],myid))
            r = rows.fetchone()
            _participants = r["participants"].split()
            participants += _participants
        except:
            pass
        try:
            if not m["chatname"]:
                raise Exception
            rows = self.conn.execute("SELECT * FROM Chats WHERE name=? and participants IS NOT NULL and participants!=?", (m["chatname"],myid))
            r = rows.fetchone()
            _participants = r["participants"].split()
            participants += _participants
        except:
            pass
        try:
            if not m["convo_id"]:
                raise Exception
            rows = self.conn.execute("SELECT author,dialog_partner,identities FROM Messages WHERE convo_id=?", (m["convo_id"],))
            _participants = u""
            for r in rows:
                _participants += r["author"] + u" " + r["dialog_partner"] + u" " + r["identities"] + u" "
            _participants = _participants.split()
            participants += _participants
        except:
            pass
        try:
            if not m["chatname"]:
                raise Exception
            rows = self.conn.execute("SELECT author,dialog_partner,identities FROM Messages WHERE chatname=?", (m["chatname"],))
            _participants = u""
            for r in rows:
                _participants += r["author"] + u" " + r["dialog_partner"] + u" " + r["identities"] + u" "
            _participants = _participants.split()
            participants += _participants
        except:
            pass
        if m["dialog_partner"] or m["author"] or m["identities"]:
            _participants = u""
            if m["dialog_partner"]:
                _participants += m["dialog_partner"] + u" "
            if m["author"]:
                _participants += m["author"] + u" "
            if m["identities"]:
                _participants += m["identities"] + u" "
            _participants = _participants.split()
            participants += _participants

        participants = filter(lambda x: x != myid, participants)
        participants = list(set(participants))
        participants.sort()
        if participants != []:
            if m["convo_id"]:
                self._m_to_participants_table_cached[m["convo_id"]] = participants
            if m["chatname"]:
                self._m_to_participants_table_cached[m["chatname"]] = participants
            return participants
        else:
            return None

    def _m_id_to_birthday(self, m, skypeid):
        try:
            rows = self.conn.execute("SELECT * FROM Contacts WHERE skypename=?", (skypeid,))
            r = rows.next()
            _birthday = time.strptime(str(r["birthday"]), "%Y%m%d")
            return unicode(time.strftime(u"%Y/%m/%d", _birthday))
        except:
            return unicode(time.strftime(u"%m/%d", time.localtime(m["timestamp"])))

    def _body_xml_normalize(self, body_xml):
        # DIRTY HACK; FIX THIS
        result_xml = body_xml
        result_xml = re.sub(u"\r\n", u"<br />", result_xml)
        result_xml = re.sub(u"\n", u"<br />", result_xml)
        result_xml = re.sub(u"\r", u"<br />", result_xml)
        result_xml = re.sub(u"[\x00-\x1F\x7F]", u"", result_xml)
        result_xml = re.sub(u"&os;", u"", result_xml)
        result_xml = u"<root>" + result_xml + u"</root>"
        return result_xml

    def _body_xml_tree_enflat(self, body_xml, allowed_tags=["a", "br"]):
        result_xml = u''
        if body_xml.tag in allowed_tags:
            result_xml += u'<%s' % (body_xml.tag,)
            for k in body_xml.attrib:
                _attrib = body_xml.attrib[k].replace(u"'", u"\\'")
                result_xml += u' %s=\'%s\'' % (k, _attrib)
            result_xml += u'>'
        result_xml += body_xml.text if body_xml.text else u''
        for subnode in body_xml:
            result_xml += self._body_xml_tree_enflat(subnode, allowed_tags)
        if body_xml.tag in allowed_tags:
            if body_xml.tag != u"br":
                result_xml += u'</%s>' % (body_xml.tag,)
        result_xml += body_xml.tail if body_xml.tail else u''
    
        return result_xml

    def debug_print_m(self, m):
        err_msg = {}
        for k in m.keys():
            try:
                err_msg[k] = u"%s" % (m[k],)
            except UnicodeDecodeError:
                err_msg[k] = u"%s" % (base64.b16encode(m[k]),)
        #self._pp_.pprint(err_msg)
        logger.debug(self._pp_.pformat(err_msg))
