#!/usr/bin/env python3

import json
from typing import Any, Union, cast

from .commandbase import CommandBase, obj_hook
from .commandresult import CommandResult


class Empty:
    pass


def classFromName(className: str) -> Any:
    return getattr(getattr(__import__("skydelsdx"), "commands"), className)


def targetClassFromName(className: str, targetId: str) -> Any:
    attribute = getattr(__import__("skydelsdx"), "plugins")
    for module in targetId.split("."):
        attribute = getattr(attribute, module)
    return getattr(getattr(attribute, "commands"), className)


def createCommand(jsonStr: str) -> CommandBase:
    try:
        values = json.loads(jsonStr, object_hook=obj_hook)
    except Exception:
        print("Failed to parse json {}".format(jsonStr))
        raise
    class_name = values[CommandBase.CmdNameKey]
    if CommandBase.CmdTargetId in values:
        MyClass = targetClassFromName(class_name, values[CommandBase.CmdTargetId])
    else:
        MyClass = classFromName(class_name)
    command: Union[Empty, CommandBase] = Empty()
    command.__class__ = MyClass
    command = cast(CommandBase, command)
    command.values = values
    return command


def createCommandResult(jsonStr: bytes) -> CommandResult:
    type(jsonStr)
    commandResult = createCommand(jsonStr.decode("UTF-8"))
    commandResult = cast(CommandResult, commandResult)
    relatedCmdJson = commandResult.values[CommandResult.RelatedCommandKey]
    commandResult.setRelatedCommand(createCommand(relatedCmdJson))
    return commandResult
