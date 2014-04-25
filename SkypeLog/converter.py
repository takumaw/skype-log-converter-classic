# This Python file uses the following encoding: utf-8
"""Converters.
"""

import time
import email.header
import email.utils
import email.mime.multipart
import email.mime.text

from .message import *
from .locales import *

class Converter:
    def __init__(self, chat=None, locale="en"):
        self.chat = chat
        self.locale = locale

    def set_chat(self, chat):
        self.chat = chat

    def set_locale(self, locale):
        self.locale = locale

    def to_string(self, code="utf-8"):
        return ""

    def write(self, fp):
        fp.write(self.to_string())

class EmailConverter(Converter):
    def to_string(self, encoding="utf-8"):
        # locale
        Loc = Locale()
        Loc.set_locale(self.locale)
        _ = Loc.get_text

        # title
        _participants_name = u", ".join([p['dispname'] for p in self.chat.messages[0].participants])
        chat_title = _(u'Chat with %(members)s', {'members': _participants_name})

        # from - to
        _participants_eml = []
        for p in self.chat.messages[0].participants:
            if p['skypeid'].startswith("1:"):
                # MSN
                _p_address = '%s' % (p['skypeid'][2:],)
            elif p['skypeid'].startswith("live:"):
                # Live
                _p_address = '%s@skype.com' % (p['skypeid'][5:],)
            elif p['skypeid'].startswith("xmpp:-"):
                # Facebook
                _p_address = '%s' % (p['skypeid'][6:],)
            else:
                # Skype
                _p_address = '%s@skype.com' % (p['skypeid'],)
            _p = '"%s" <%s>' % (email.header.Header(p['dispname'], encoding), _p_address)
            _participants_eml.append(_p)
        _participants_eml = ", ".join(_participants_eml)
        
        chat_to = '"%s" <%s>' % (email.header.Header(self.chat.dispname, encoding),
                                '%s@skype.com' % (self.chat.skypeid,))
        chat_from = None
        chat_cc = None
        if len(self.chat.messages[0].participants) == 1:
            chat_from = _participants_eml
        else:
            chat_from = chat_to
            chat_cc = _participants_eml
    
        # date
        chat_date = self.chat.messages[0].timestamp

        # body
        chat_lines = []
        _last_type = -1
        _last_timestamp = ""
        _last_skypeid = ""
        
        for m in self.chat.messages:
            # type
            _type = m.msgtype
            _chatmsg_type = m.chatmsg_type

            # dispname
            _skypeid = m.skypeid
            _dispname = m.dispname
            
            # timestamp
            _timestamp = unicode(time.strftime("%H:%M" , m.timestamp))

            # chat_body
            if _type == MSGTYPE_SETTOPIC:
                # set topic
                if _chatmsg_type == 5:
                    # set topic
                    _message = _(m.message, m.message_formatdict)
                    chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                    u'<tbody>' + \
                                    u'<tr>' + \
                                    u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                    u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                    u'</tr>' + \
                                    u'<tr>' + \
                                    u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                    u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                    u'</tr>' + \
                                    u'</tbody>' + \
                                    u'</table>'
                elif _chatmsg_type == 15:
                    # set group picture
                    _message = _(m.message, m.message_formatdict)
                    chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                    u'<tbody>' + \
                                    u'<tr>' + \
                                    u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                    u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                    u'</tr>' + \
                                    u'<tr>' + \
                                    u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                    u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                    u'</tr>' + \
                                    u'</tbody>' + \
                                    u'</table>'
            elif _type == MSGTYPE_CREATEGROUPROOM:
                # invoke a new group room (from this window)
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_MEMBER_ADD:
                # add new member(s)
                # author invite identities
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_MEMBER_KICK:
                # kick a member
                # add new member(s)
                # author invite identities
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_SETROLE:
                # set role
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_CALL_START:
                # start call
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:10%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:90%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_CALL_END:
                # end call
                if m.message_formatdict:
                    _message = _(m.message, m.message_formatdict)
                else:
                    _message = _(m.message)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:10%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:90%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_CONTACTINFO_REQ:
                # require contact info
                _message = _(m.message, m.message_formatdict)
                _message_body = m.message_body
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;" colspan="3">' + _message_body + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_CONTACTINFO_ACK:
                # share contact info
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_BLOCK:
                # block a member
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_ME:
                # Skype command /me ...
                _message_body = m.message_body
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:100%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#000">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;text-align:center;">' + _message_body + u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_MSG:
                _message_body = m.message_body
            
                # message
                chat_line = u'<div>'

                # add timestamp
                if _type == _last_type and _timestamp == _last_timestamp:
                    chat_line += u'<span style="display:block;float:left;color:#888">&nbsp;</span>'
                else:
                    chat_line += u'<span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span>'
                
                # add message body begin
                if _type == _last_type and _skypeid == _last_skypeid:
                    chat_line += u'<span style="display:block;padding-left:6em"><span>'
                else:
                    chat_line += u'<span style="display:block;padding-left:6em;text-indent:-1em"><span>'
                    chat_line += u'<span style="font-weight:bold" dir="ltr">' + _dispname + u'</span>: '

                # add message body
                chat_line += _message_body
                
                # add message body end
                chat_line += u'</span></span>'
                chat_line += u'</div>'
            elif _type == MSGTYPE_SENDCONTACT:
                # send contacts(s)
                _message = _(m.message, m.message_formatdict)
                _message_body = m.message_body
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                    u'<tbody>' + \
                    u'<tr>' + \
                    u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                    u'<td style="font-size:1;width:10%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                    u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                    u'<td style="font-size:1;width:90%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                    u'</tr>' + \
                    u'<tr>' + \
                    u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                    u'<td style="font-size:80%;color:#aaa;width:100%;" colspan="3">' + \
                    _message_body + \
                    u'</td>' + \
                    u'</tr>' + \
                    u'</tbody>' + \
                    u'</table>'
            elif _type == MSGTYPE_SENDFILE:
                # send file(s)
                _message = _(m.message, m.message_formatdict)
                _message_body = m.message_body
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:10%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:90%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">&nbsp;&nbsp;</span></td>' + \
                                u'<td style="font-size:80%;color:#aaa;width:100%;" colspan="3">' + \
                                _message_body + \
                                u'</td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_VIDEOMSG:
                # video message
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:10%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:90%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'
            elif _type == MSGTYPE_BIRTHDAY:
                # birthday
                _message = _(m.message, m.message_formatdict)
                chat_line = u'<table cellpadding="0" cellspacing="1">' + \
                                u'<tbody>' + \
                                u'<tr>' + \
                                u'<td nowrap=""><span style="display:block;float:left;color:#888">' + _timestamp + u'&nbsp;</span></td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'<td nowrap="" style="font-size:80%;color:#aaa">' + _message + u'</td>' + \
                                u'<td style="font-size:1;width:50%"><hr noshade="" size="1" color="#cccccc"></td>' + \
                                u'</tr>' + \
                                u'</tbody>' + \
                                u'</table>'

            chat_lines.append(chat_line)
            _last_type = _type
            _last_timestamp = _timestamp
            _last_skypeid = _skypeid

        chat_body = u"".join(chat_lines)

        # generate email
        eml = email.mime.multipart.MIMEMultipart('alternative')
        eml['date'] = email.utils.formatdate(time.mktime(chat_date), True)
        eml['From'] = chat_from
        eml['To'] = chat_to
        if chat_cc != None:
            eml['CC'] = chat_cc
        eml['Subject'] = '%s' % email.header.Header(chat_title, encoding)

        #plain_part = email.mime.text.MIMEText(..., 'plain')
        html_part = email.mime.text.MIMEText(chat_body, 'html', encoding)
        #msg.attach(plain_part)
        eml.attach(html_part)

        return eml.as_string()