# This Python file uses the following encoding: utf-8
"""Locale: Japanese
"""

class LocaleDict:
    def get_text(self, text, formatdict=None):
        # translate
        if text == u'Chat with %(members)s':
            translated_text = u'%(members)s さんとのチャット' % formatdict
        elif text == u'%(author)s set topic to "%(topic)s"':
            translated_text = u'%(author)s がタイトルを "%(topic)s" に設定しました' % formatdict
        elif text == u'%(author)s updated the group picture':
            translated_text = u'%(author)s が新規ピクチャを設定しました' % formatdict
        elif text == u'%(author)s created a group conversation':
            translated_text = u'%(author)s はこのダイヤログから会議 グループ会話 を開始しました' % formatdict
        elif text == u'%(author)s added %(identities)s to this conversation':
            translated_text = u'%(author)s が %(identities)s を会話に追加しました' % formatdict
        elif text == u'%(author)s has ejected %(identities)s from this conversation':
            translated_text = u'%(author)s はこの会話から %(identities)s を追放しました' % formatdict
        elif text == u'%(author)s has left the conversation':
            translated_text = u'%(author)s が会話を退席しました' % formatdict
        elif text == u'%(author)s set rank of %(identities)s to %(role)s':
            translated_formatdict = formatdict
            if translated_formatdict["role"] == u"Spectator":
                translated_formatdict["role"] = u"傍観者"
            elif translated_formatdict["role"] == u"Speaker":
                translated_formatdict["role"] = u"話す人"
            elif translated_formatdict["role"] == u"Administrator":
                translated_formatdict["role"] = u"管理者"
            translated_text = u'%(author)s は %(identities)s のランクを %(role)s に設定しました' % translated_formatdict
        elif text == u'Call started':
            translated_text = u'通話を開始しました'
        elif text == u'Call started by %(author)s':
            translated_text = u'%(author)s が通話を開始しました' % formatdict
        elif text == u'Call ended':
            translated_text = u'通話終了'
        elif text == u'Call ended - %(reason)s':
            translated_formatdict = formatdict
            if translated_formatdict["reason"] == u"Busy":
                translated_formatdict["reason"] = u"取り込み中"
            elif translated_formatdict["reason"] == u"No answer":
                translated_formatdict["reason"] = u"応答なし"
            elif translated_formatdict["reason"] == u"Connection dropped":
                translated_formatdict["reason"] = u"接続切断"
            elif translated_formatdict["reason"] == u"Unable to connect":
                translated_formatdict["reason"] = u"接続出来ませんでした"
            elif translated_formatdict["reason"] == u"Internal Error":
                translated_formatdict["reason"] = u"内部エラー"
            elif translated_formatdict["reason"] == u"Insufficient Funds":
                translated_formatdict["reason"] = u"残高不足"
            elif translated_formatdict["reason"] == u"Unknown":
                translated_formatdict["reason"] = u"不明"
            translated_text = u'通話終了 - %(reason)s' % translated_formatdict
        elif text == u'Contact request':
            translated_text = u'コンタクト追加要求'
        elif text == u'%(author)s has shared contact details with %(identities)s.':
            translated_text = u'%(author)s が %(identities)s と連絡先情報を共有しました' % formatdict
        elif text == u'Blocked contact':
            translated_text = u'ブロックした連絡先'
        elif text == u'%(author)s sent you contact(s)':
            translated_text = u'%(author)s が連絡先を送信しました' % formatdict
        elif text == u'%(author)s sent you file(s)':
            translated_text = u'%(author)s がファイルを送信しました' % formatdict
        elif text == u'%(author)s sent you a video message':
            translated_text = u'%(author)s がビデオメッセージを送信しました' % formatdict
        elif text == u"It's %(author)s's birthday on %(date)s":
            translated_text = u'%(date)s は %(author)s の誕生日です' % formatdict

        return translated_text
