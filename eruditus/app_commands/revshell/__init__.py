import json
import os
import string
from typing import Optional

import discord
from discord import app_commands
from discord.app_commands import Choice

from lib.types import OSType


class Revshell(app_commands.Command):
    # https://github.com/0dayCTF/reverse-shell-generator/blob/main/js/data.js
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/revshells.json", encoding="utf-8"
    ) as fp:
        payloads = json.load(fp)

    shells = {
        "sh",
        "/bin/sh",
        "bash",
        "/bin/bash",
        "cmd",
        "powershell",
        "pwsh",
        "ash",
        "bsh",
        "csh",
        "ksh",
        "zsh",
        "pdksh",
        "tcsh",
        "mksh",
        "dash",
    }

    def __init__(self):
        super().__init__(
            name="revshell",
            description="Generate a reverse shell payload.",
            callback=self.cmd_callback,  # type: ignore
        )

        @self.autocomplete("shell")
        async def _shell_autocompletion_func(
            interaction: discord.Interaction, current: str
        ) -> list[Choice[str]]:
            """Autocomplete shell name.

            Args:
                interaction: The interaction that triggered this command.
                current: The shell name typed so far.

            Returns:
                A list of suggestions.
            """
            suggestions = []
            for shell in Revshell.shells:
                if current.lower() in shell.lower():
                    suggestions.append(Choice(name=shell, value=shell))
                if len(suggestions) == 25:
                    break
            return suggestions

        @self.autocomplete("name")
        async def _name_autocompletion_func(
            interaction: discord.Interaction, current: str
        ) -> list[Choice[str]]:
            """Autocomplete reverse shell payload name.

            Args:
                interaction: The interaction that triggered this command.
                current: The reverse shell name typed so far.

            Returns:
                A list of suggestions.
            """
            suggestions = []
            platform = OSType(interaction.namespace.platform).name
            for payload in Revshell.payloads[platform]:
                if current.lower() in payload.lower():
                    suggestions.append(Choice(name=payload, value=payload))
                if len(suggestions) == 25:
                    break
            return suggestions

    async def cmd_callback(
        self,
        interaction: discord.Interaction,
        platform: OSType,
        name: str,
        ip: str,
        port: int,
        shell: Optional[str] = "/bin/bash",
    ) -> None:
        """Generate a reverse shell payload.

        Args:
            interaction: The interaction that triggered this command.
            platform: The platform where the reverse shell payload is executed.
            name: The payload name.
            ip: The IP address that the shell will connect to.
            port: The port number that the shell will connect to.
            shell: The shell to use, if applicable (default: /bin/bash).
        """
        if name not in Revshell.payloads[platform.name]:
            await interaction.response.send_message(
                f"No such payload for platform: {platform.name}", ephemeral=True
            )
            return

        template = Revshell.payloads[platform.name][name]
        for _, placeholder, _, _ in string.Formatter().parse(template):
            if placeholder == "shell":
                payload = template.format(ip=ip, port=port, shell=shell)
                break
        else:
            payload = template.format(ip=ip, port=port)
        await interaction.response.send_message(f"```sh\n{payload}\n```")
