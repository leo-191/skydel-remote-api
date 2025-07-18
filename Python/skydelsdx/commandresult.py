#!/usr/bin/env python3

from typing import Literal, Optional, Protocol, Union, cast

from .commandbase import CommandBase


class FailedCommand(Protocol):
    def isSuccess(self) -> Literal[False]: ...
    def errorMsg(self) -> str: ...


class CommandResult(CommandBase):
    RelatedCommandKey = "RelatedCommand"

    def __init__(self, cmd_name: str) -> None:
        CommandBase.__init__(self, cmd_name)
        self.command: Optional[CommandBase] = None

    def isSuccess(self) -> bool:
        return True

    def getMessage(self: Union["CommandResult", FailedCommand]) -> str:
        if not self.isSuccess():
            self = cast(FailedCommand, self)
            return self.errorMsg()
        elif self.__class__.__name__ == "SuccessResult":
            return "Success"
        else:
            self = cast(CommandResult, self)
            return self.toString()

    def setRelatedCommand(self, cmd: CommandBase) -> None:
        self.command = cmd

    def getRelatedCommand(self) -> Optional[CommandBase]:
        return self.command

    def toString(self) -> str:
        if len(self.values) == 2:
            return self.getName() + "()"
        cmdStr = self.getName() + "("
        for key, value in self.values.items():
            if (
                key != CommandBase.CmdNameKey
                and key != CommandBase.CmdUuidKey
                and key != CommandResult.RelatedCommandKey
            ):
                cmdStr += key + ": " + str(value) + ", "
        return cmdStr[:-2] + ")"
