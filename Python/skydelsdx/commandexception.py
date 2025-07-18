from typing import cast

from .commandbase import CommandBase
from .commandresult import CommandResult


class CommandException(Exception):
    def __init__(
        self, command_result: CommandResult, simulation_error_msg: str
    ) -> None:
        # Call the base class constructor with the parameters it needs
        msg = (
            cast(CommandBase, command_result.getRelatedCommand()).getName()
            + " failed: "
            + command_result.getMessage()
            + simulation_error_msg
        )
        super(CommandException, self).__init__(msg)
        self.command_result = command_result
        self.simulation_error_msg = simulation_error_msg

    def getCommandResult(self) -> CommandResult:
        return self.command_result

    def getSimulationErrorMsg(self) -> str:
        return self.simulation_error_msg
