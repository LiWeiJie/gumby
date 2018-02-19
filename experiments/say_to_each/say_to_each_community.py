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

from time import time


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
        self.start_time = time()
        self._response_to_broadcast_ct = 0
        self._response_dict = {}
        self._broadcaster = []


    def initiate_conversions(self):
        return [DefaultConversion(self), SayToEachCommunityConversion(self)]

    def initiate_meta_messages(self):
        messages = super(SayToEachCommunity, self).initiate_meta_messages()

        ourmessages = [Message(self,
                               u"say-broadcast",
                               MemberAuthentication(),
                               PublicResolution(),
                               FullSyncDistribution(u"ASC", 128, False),
                               CommunityDestination(10),
                               SayToOthersPayload(),
                               self._generic_timeline_check,
                               self.on_say_broadcast,
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
                               batch=BatchConfiguration(0.0)),
                       Message(self,
                               u"response-to-broadcast",
                               MemberAuthentication(),
                               PublicResolution(),
                               DirectDistribution(),
                               CandidateDestination(),
                               SayToOthersPayload(),
                               self._generic_timeline_check,
                               self.on_response_to_broadcast,
                               batch=BatchConfiguration(0.0))
                       ]
        messages.extend(ourmessages)

        return messages

    def on_say(self, messages):
        for message in messages:
            self.guestbook.append( message.payload.who + " say : " + message.payload.text )

    def on_say_broadcast(self, messages):
        for message in messages:
            print("%s say to me at %d: %s" % (message.payload.who, time()-self.start_time, message.payload.text))
            print("Received broadcast from node %s" % (
                             message.candidate.get_member().public_key.encode("hex")[-8:],
                             ))
            print(message.authentication.member.public_key)
            print(message.authentication.member.private_key)
            # response to broadcast
            self._broadcaster.append(message.candidate)
            # self.say_response_to_broadcast(message.candidate, "")

            # self.guestbook.append( message.payload.who + " say : " + message.payload.text )


    def on_response_to_broadcast(self, messages):
        for message in messages:
            # self.logger.info("Received response_to_broadcast from node %s for sequence number %d",
            #                  message.candidate.get_member().public_key.encode("hex")[-8:],
            #                  message.payload.requested_sequence_number)
            if (message.payload.who) in self._response_dict:
                print("rereceived broadcast reponse")
            else:
                self._response_dict[message.payload.who] = True
                self._response_to_broadcast_ct += 1
            # print("%s say to me at %d: %s"%(message.payload.who, self.start_time, message.payload.text))

    @property
    def response_to_broadcast_ct(self):
        return self._response_to_broadcast_ct

    def say_response_to_broadcast(self, candidate, msg):
        meta = self.get_meta_message(u"response-to-broadcast")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            destination=(candidate,),
                            payload=(self.my_member.__str__(), msg))
        self.dispersy.store_update_forward([message], False, False, True)

    def say_broadcast(self, msg):
        self._response_to_broadcast_ct = 0
        self._response_dict = {}
        meta = self.get_meta_message(u"say-broadcast")
        message = meta.impl(authentication=(self._my_member,),
                            distribution=(self.claim_global_time(),),
                            payload=(self.my_member.__str__(), msg))
        print("broadcast at %d"%(time()-self.start_time))
        self.dispersy.store_update_forward([message], False, False, True)

    def say_to_locals(self):
        meta = self.get_meta_message(u"say-to-locals")
        messages = []
        for candidate in self.dispersy_yield_verified_candidates():
            messages.append(meta.impl(authentication=(self._my_member,),
                                      distribution=(self.claim_global_time(),),
                                      destination=(candidate,),
                                      payload=(self.my_member.__str__(), "hello")))
        self.dispersy.store_update_forward(messages, False, False, True)

    def write_down_neighbors(self):
        # veris = self.dispersy_yield_verified_candidates()
        walk_ct = stumble_ct = intro_ct = dis_ct = timeout_ct =0
        now = time()
        for candidate in self._candidates.itervalues():
            cate = candidate.get_category(now)
            if cate == u"walk":
                walk_ct += 1
            elif cate == u"stumble":
                stumble_ct += 1
            elif cate == u"intro":
                intro_ct += 1
            elif cate == u"discovered":
                dis_ct += 1
            else:
                timeout_ct += 1

        print "%d : <Total candidates : %d, walk node: %d, stumble node: %d, intro node %d, discovered node: %d, timeout node: %d>"%(now - self.start_time, self._candidates.__len__(), walk_ct, stumble_ct, intro_ct, dis_ct, timeout_ct)
        



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
            community.get_meta_message(u"say-broadcast"),
            self._encode_say,
            self._decode_say)
        self.define_meta_message(
            chr(2),
            community.get_meta_message(u"say-to-locals"),
            self._encode_say,
            self._decode_say)
        self.define_meta_message(
            chr(3),
            community.get_meta_message(u"response-to-broadcast"),
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
