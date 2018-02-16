import random
import struct

from Tribler.dispersy.authentication import MemberAuthentication
from Tribler.dispersy.community import Community
from Tribler.dispersy.conversion import BinaryConversion, DefaultConversion
from Tribler.dispersy.destination import CandidateDestination, CommunityDestination
from Tribler.dispersy.distribution import FullSyncDistribution, DirectDistribution
from Tribler.dispersy.message import BatchConfiguration, Message
from Tribler.dispersy.payload import Payload
from Tribler.dispersy.resolution import PublicResolution

from Tribler.Core.Utilities.encoding import encode, decode


class SayToEachCommunity(Community):

    # @classmethod
    # def get_master_members(cls, dispersy):
    #     master_key = "<public-key>".decode("HEX")
    #     master = dispersy.get

    def __init__(self, dispersy, master_member, my_member):
        super(SayToEachCommunity, self).__init__(dispersy, master_member, my_member)

        self.modulus = 1000
        self.n = 5
        self.guestbook = []

    def initiate_conversions(self):
        return [DefaultConversion(self), SayToEachCommunityConversion(self)]

    def initiate_meta_messages(self):
        messages = super(SayToEachCommunity, self).initiate_meta_messages()

        ourmessages = [Message(self,
                               u"say-to-others",
                               MemberAuthentication(),
                               PublicResolution(),
                               FullSyncDistribution(u"ASC", 128, False),
                               CommunityDestination(10),
                               SayToOthersPayload(),
                               self._generic_timeline_check,
                               self.on_say,
                               batch=BatchConfiguration(0.0)),
                       Message(self,
                               u"say-to-locals",
                               MemberAuthentication(),
                               PublicResolution(),
                               DirectDistribution(),
                               CandidateDestination(),
                               SayToOthersPayload(),
                               self._generic_timeline_check,
                               self.on_say,
                               batch=BatchConfiguration(0.0))
                       ]
        messages.extend(ourmessages)

        return messages

    def on_say(self, messages):
        for message in messages:
            self.guestbook.append( message.payload.who + " say : " + message.payload.text )

    def say_to_others(self):
        meta = self.get_meta_message(u"say-to-others")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            payload=(self.my_member.__str__(), "hello"))
        self.dispersy.store_update_forward([message], False, False, True)

    def write_down_neighbors(self):
        # veris = self.dispersy_yield_verified_candidates()
        print "candidates : %d"%self._candidates.__len__()
        for candidate in self.dispersy_yield_candidates():
            print candidate

    def say_to_locals(self):
        meta = self.get_meta_message(u"say-to-locals")
        messages = []
        for candidate in self.dispersy_yield_verified_candidates():
            messages.append(meta.impl(authentication=(self._my_member,),
                                      distribution=(self.claim_global_time(),),
                                      destination=(candidate,),
                                      payload=(self.my_member.__str__(), "hello")))
        self.dispersy.store_update_forward(messages, False, False, True)

class SayToOthersPayload(Payload):
    class Implementation(Payload.Implementation):
        def __init__(self, meta, who, text):
            assert isinstance(who, str)
            assert isinstance(text, str)            
            super(SayToOthersPayload.Implementation, self).__init__(meta)
            self._who = who
            self._text = text

        @property
        def who(self):
            return self._who
        
        @property
        def text(self):
            return self._text
 

class SayToEachCommunityConversion(BinaryConversion):

    def __init__(self, community):
        super(SayToEachCommunityConversion, self).__init__(community, "\x01")
        self.define_meta_message(
            chr(1),
            community.get_meta_message(u"say-to-others"),
            self._encode_say,
            self._decode_say)
        self.define_meta_message(
            chr(2),
            community.get_meta_message(u"say-to-locals"),
            self._encode_say,
            self._decode_say)

    def _encode_say(self, message):
        return encode((message.payload.who, message.payload.text)),

    def _decode_say(self, placeholder, offset, data):
        try:
            offset, payload = decode(data, offset)
        except ValueError:
            raise DropPacket("Unable to decode the say-payload")

        if not isinstance(payload, tuple):
            raise DropPacket("Invalid payload type")

        who, text = payload
        if not isinstance(text, str):
            raise DropPacket("Invalid 'text' type")
        if not isinstance(who, str):
            raise DropPacket("Invalid 'who' type")

        return offset, placeholder.meta.payload.implement(who, text)
        # value, = self.share_format.unpack_from(data, offset)
        # offset += self.share_format.size
        # return offset, placeholder.meta.payload.implement(value)
