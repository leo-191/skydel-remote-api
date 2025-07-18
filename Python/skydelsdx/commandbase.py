#!/usr/bin/env python3

import datetime
import json
import uuid
from enum import IntFlag
from typing import Any, Optional, Union


class ExecutePermission(IntFlag):
    EXECUTE_IF_IDLE = 1 << 1
    EXECUTE_IF_SIMULATING = 1 << 2
    EXECUTE_IF_NO_CONFIG = 1 << 3


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return {
                "Spec": "UTC",
                "Year": o.year,
                "Month": o.month,
                "Day": o.day,
                "Hour": o.hour,
                "Minute": o.minute,
                "Second": o.second,
            }
        elif isinstance(o, datetime.date):
            return {"Year": o.year, "Month": o.month, "Day": o.day}
        elif isinstance(o, CommandBase):
            return o.values
        elif hasattr(o, "__dict__"):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)


class MakeObj:
    def __init__(self, dict: dict) -> None:
        self.__dict__ = dict

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        return repr(self.__dict__)

    def __setitem__(self, key, item) -> None:
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __eq__(self, other) -> bool:
        if isinstance(other, MakeObj):
            return self.items() == other.items()
        return False

    def __contains__(self, key) -> bool:
        return key in self.__dict__

    def iteritems(self):
        return self.__dict__.items()

    def items(self):
        return self.__dict__.items()


def obj_hook(d: dict) -> Union[datetime.datetime, datetime.date, MakeObj]:
    if all(field in d for field in ["Year", "Month", "Day"]):
        if all(field in d for field in ["Spec", "Hour", "Minute", "Second"]):
            return datetime.datetime(
                d["Year"], d["Month"], d["Day"], d["Hour"], d["Minute"], d["Second"]
            )
        else:
            return datetime.date(d["Year"], d["Month"], d["Day"])
    else:
        return MakeObj(d)


class CommandBase:
    CmdNameKey = "CmdName"
    CmdUuidKey = "CmdUuid"
    CmdTimestampKey = "CmdTimestamp"
    CmdTargetId = "CmdTargetId"

    def __init__(
        self, cmd_name: Optional[str] = None, target_id: Optional[str] = None
    ) -> None:
        self.values = {}
        if cmd_name:
            self.values[CommandBase.CmdNameKey] = cmd_name
            self.values[CommandBase.CmdUuidKey] = "{" + uuid.uuid1().urn[9:] + "}"
        if target_id:
            self.values[CommandBase.CmdTargetId] = target_id

    def executePermission(self) -> "ExecutePermission":
        return ExecutePermission.EXECUTE_IF_IDLE

    # TODO: unknown flags
    def hasExecutePermission(self, flags) -> bool:
        return (self.executePermission() & flags) == flags

    def setTimestamp(self, timestamp):
        self.values[CommandBase.CmdTimestampKey] = timestamp

    def set(self, key: str, val: Any) -> None:
        self.values[key] = val

    def get(self, key: str) -> Any:
        return self.values[key]

    def getName(self) -> str:
        return self.values[CommandBase.CmdNameKey]

    def getUuid(self) -> str:
        return self.values[CommandBase.CmdUuidKey]

    def parse(self, jsonStr: str) -> None:
        print("Parsing", jsonStr)
        self.values = json.loads(jsonStr, object_hook=obj_hook)

    def toJson(self) -> str:
        return json.dumps(self.values, cls=Encoder)

    def toString(self) -> str:
        if len(self.values) == 2:
            return self.getName() + "()"
        cmdStr = self.getName() + "("
        for key, value in self.values.items():
            if key != CommandBase.CmdNameKey and key != CommandBase.CmdUuidKey:
                cmdStr += key + ": " + str(value) + ", "
        return cmdStr[:-2] + ")"

    def deprecated(self) -> Optional[str]:
        return None
