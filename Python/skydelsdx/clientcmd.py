#!/usr/bin/env python3

import struct

from .client import Client
from .commandfactory import *
from .commands import *


class MsgId:
    Command = 0
    Result = 1
    ApiVersion = 2


class ClientCmd(Client):
    def __init__(self, address: str, port: int) -> None:
        Client.__init__(self, address, port, True)

    def _getPacketSize(self) -> int:
        return struct.unpack("<H", self._getPacket(2))[0]

    def _sendMessage(self, message: bytes) -> None:
        packet = struct.pack("<H", len(message)) + message
        self.sock.sendall(packet)

    def getServerApiVersion(self) -> int:
        message = self._msgId2Packet(MsgId.ApiVersion) + struct.pack("<I", ApiVersion)
        self._sendMessage(message)

        while 1 == 1:
            msgSize = self._getPacketSize()
            msgId = self._getPacketMsgId()

            if msgId == MsgId.ApiVersion:
                return struct.unpack("<I", self._getPacket(4))[0]
            else:
                self._getPacket(msgSize - 1)

        assert False, "Unreachable code"

    def sendCommand(self, cmd: CommandBase) -> None:
        json_str = cmd.toJson()

        message = (self._msgId2Packet(MsgId.Command)) + (json_str + "\0").encode(
            "UTF-8"
        )
        self._sendMessage(message)

    def waitCommand(self, cmd: CommandBase) -> CommandResult:
        while 1 == 1:
            msgSize = self._getPacketSize()
            msgId = self._getPacketMsgId()

            if msgId == MsgId.Result:
                msg_json_len = struct.unpack("<i", self._getPacket(4))[0]
                msg_json = self._getPacket(msg_json_len)[:-1]
                result = createCommandResult(msg_json)
                if cmd.getUuid() == result.getRelatedCommand().getUuid():
                    return result
            else:
                self._getPacket(msgSize - 1)  # skip the packet

        assert False, "Unreachable code"
