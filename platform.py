# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import subprocess
import sys

from platformio import exception
from platformio.public import PlatformBase, get_systype


class Linux_armPlatform(PlatformBase):

    @staticmethod
    def _is_native():
        systype = get_systype()
        return "linux_arm" in systype or "linux_aarch64" in systype

    @property
    def packages(self):
        packages = PlatformBase.packages.fget(self)
        systype = get_systype()
        # PlatformIO's toolchain package only works on macOS x86_64
        # All other platforms use system-installed toolchains
        if systype != "darwin_x86_64" and "toolchain-gccarmlinuxgnueabi" in packages:
            del packages['toolchain-gccarmlinuxgnueabi']
        return packages

    def configure_default_packages(self, variables, targets):
        if not self._is_native() and "wiringpi" in variables.get(
                "pioframework", []):
            raise exception.PlatformioException(
                "PlatformIO temporary does not support cross-compilation "
                "for WiringPi framework. Please use PIO Core directly on "
                "Raspberry Pi")
        return super().configure_default_packages(variables, targets)

    def on_upload(self, target, source, env):
        """
        Custom upload handler for Linux ARM platform.
        Supports multiple upload protocols: scp, rsync, ssh
        """
        upload_protocol = env.GetProjectOption("upload_protocol", "manual")

        if upload_protocol == "scp":
            return self._upload_scp(target, source, env)
        elif upload_protocol == "rsync":
            return self._upload_rsync(target, source, env)
        elif upload_protocol == "ssh":
            return self._upload_ssh(target, source, env)
        elif upload_protocol == "manual":
            print("\n" + "="*60)
            print("MANUAL UPLOAD REQUIRED")
            print("="*60)
            print("\nCompiled binary location:")
            print(f"  {source[0]}")
            print("\nTo deploy to your target device, use one of:")
            print(f"  scp {source[0]} user@host:/path/to/destination")
            print(f"  rsync -avz {source[0]} user@host:/path/to/destination")
            print("\nTo configure automatic upload, add to platformio.ini:")
            print("  upload_protocol = scp")
            print("  upload_port = user@hostname:/path/to/destination")
            print("\nSee documentation for more upload options.")
            print("="*60 + "\n")
            return 0
        else:
            raise exception.PlatformioException(
                f"Unknown upload protocol '{upload_protocol}'. "
                "Supported protocols: scp, rsync, ssh, manual"
            )

    def _check_upload_tool(self, tool_name):
        """Check if required upload tool is available."""
        if not shutil.which(tool_name):
            raise exception.PlatformioException(
                f"Upload tool '{tool_name}' is not installed. "
                f"Please install it using your system package manager:\n"
                f"  Linux: sudo apt install {tool_name}\n"
                f"  macOS: brew install {tool_name}"
            )

    def _parse_upload_port(self, upload_port, env):
        """
        Parse upload_port into components.
        Supported formats:
          - user@host:/path/to/destination
          - user@host
          - host:/path
          - host
        Returns: (user, host, path)
        """
        if not upload_port:
            raise exception.PlatformioException(
                "upload_port is not configured. Add to platformio.ini:\n"
                "  upload_port = user@hostname:/path/to/destination"
            )

        # Parse user@host:path format
        user = env.GetProjectOption("upload_user", "pi")
        path = env.GetProjectOption("upload_path", "/tmp/program")

        # Extract user if specified in upload_port
        if "@" in upload_port:
            user_part, host_part = upload_port.split("@", 1)
            user = user_part
        else:
            host_part = upload_port

        # Extract host and path
        if ":" in host_part:
            host, path_part = host_part.split(":", 1)
            path = path_part
        else:
            host = host_part

        return user, host, path

    def _upload_scp(self, target, source, env):
        """Upload binary using SCP (Secure Copy Protocol)."""
        self._check_upload_tool("scp")

        upload_port = env.GetProjectOption("upload_port", None)
        user, host, path = self._parse_upload_port(upload_port, env)

        ssh_port = env.GetProjectOption("upload_ssh_port", "22")
        ssh_key = env.GetProjectOption("upload_ssh_key", None)
        upload_flags = env.GetProjectOption("upload_flags", "")

        # Build SCP command
        cmd = ["scp"]

        # Add SSH port
        cmd.extend(["-P", str(ssh_port)])

        # Add SSH key if specified
        if ssh_key:
            key_path = os.path.expanduser(ssh_key)
            if not os.path.exists(key_path):
                raise exception.PlatformioException(
                    f"SSH key file not found: {key_path}"
                )
            cmd.extend(["-i", key_path])

        # Add custom flags
        if upload_flags:
            cmd.extend(upload_flags.split())

        # Add source and destination
        cmd.append(str(source[0]))
        cmd.append(f"{user}@{host}:{path}")

        print("\n" + "="*60)
        print("UPLOADING VIA SCP")
        print("="*60)
        print(f"Source:      {source[0]}")
        print(f"Destination: {user}@{host}:{path}")

        # Show final executable path for clarity
        program_name = os.path.basename(str(source[0]))
        if path.endswith('/'):
            final_path = os.path.join(path, program_name)
            print(f"Program:     {final_path}")
        else:
            print(f"Program:     {path}")

        print(f"SSH Port:    {ssh_port}")
        if ssh_key:
            print(f"SSH Key:     {ssh_key}")
        print("="*60 + "\n")

        # Execute SCP command
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode != 0:
            raise exception.PlatformioException(
                f"SCP upload failed with exit code {result.returncode}"
            )

        print("\n" + "="*60)
        print("UPLOAD SUCCESSFUL")
        print("="*60 + "\n")

        # Post-upload execution if configured
        if env.GetProjectOption("upload_run_after", False):
            return self._run_remote_command(user, host, ssh_port, ssh_key, path, env)

        return 0

    def _upload_rsync(self, target, source, env):
        """Upload binary using rsync (efficient incremental transfer)."""
        self._check_upload_tool("rsync")

        upload_port = env.GetProjectOption("upload_port", None)
        user, host, path = self._parse_upload_port(upload_port, env)

        ssh_port = env.GetProjectOption("upload_ssh_port", "22")
        ssh_key = env.GetProjectOption("upload_ssh_key", None)
        upload_flags = env.GetProjectOption("upload_flags", "-avz")

        # Build rsync command
        cmd = ["rsync"]

        # Add flags (default: -avz for archive, verbose, compress)
        if upload_flags:
            cmd.extend(upload_flags.split())

        # Add SSH options
        ssh_opts = f"-p {ssh_port}"
        if ssh_key:
            key_path = os.path.expanduser(ssh_key)
            if not os.path.exists(key_path):
                raise exception.PlatformioException(
                    f"SSH key file not found: {key_path}"
                )
            ssh_opts += f" -i {key_path}"

        cmd.extend(["-e", f"ssh {ssh_opts}"])

        # Add source and destination
        cmd.append(str(source[0]))
        cmd.append(f"{user}@{host}:{path}")

        print("\n" + "="*60)
        print("UPLOADING VIA RSYNC")
        print("="*60)
        print(f"Source:      {source[0]}")
        print(f"Destination: {user}@{host}:{path}")

        # Show final executable path for clarity
        program_name = os.path.basename(str(source[0]))
        if path.endswith('/'):
            final_path = os.path.join(path, program_name)
            print(f"Program:     {final_path}")
        else:
            print(f"Program:     {path}")

        print(f"SSH Port:    {ssh_port}")
        if ssh_key:
            print(f"SSH Key:     {ssh_key}")
        print(f"Flags:       {upload_flags}")
        print("="*60 + "\n")

        # Execute rsync command
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode != 0:
            raise exception.PlatformioException(
                f"Rsync upload failed with exit code {result.returncode}"
            )

        print("\n" + "="*60)
        print("UPLOAD SUCCESSFUL")
        print("="*60 + "\n")

        # Post-upload execution if configured
        if env.GetProjectOption("upload_run_after", False):
            return self._run_remote_command(user, host, ssh_port, ssh_key, path, env)

        return 0

    def _upload_ssh(self, target, source, env):
        """
        Upload binary using SSH with piped input.
        This method uses SSH with cat to transfer the file.
        """
        self._check_upload_tool("ssh")

        upload_port = env.GetProjectOption("upload_port", None)
        user, host, path = self._parse_upload_port(upload_port, env)

        ssh_port = env.GetProjectOption("upload_ssh_port", "22")
        ssh_key = env.GetProjectOption("upload_ssh_key", None)

        # Build SSH command to receive file via stdin
        cmd = ["ssh"]
        cmd.extend(["-p", str(ssh_port)])

        if ssh_key:
            key_path = os.path.expanduser(ssh_key)
            if not os.path.exists(key_path):
                raise exception.PlatformioException(
                    f"SSH key file not found: {key_path}"
                )
            cmd.extend(["-i", key_path])

        cmd.append(f"{user}@{host}")
        cmd.append(f"cat > {path} && chmod +x {path}")

        print("\n" + "="*60)
        print("UPLOADING VIA SSH")
        print("="*60)
        print(f"Source:      {source[0]}")
        print(f"Destination: {user}@{host}:{path}")

        # Show final executable path for clarity
        program_name = os.path.basename(str(source[0]))
        if path.endswith('/'):
            final_path = os.path.join(path, program_name)
            print(f"Program:     {final_path}")
        else:
            print(f"Program:     {path}")

        print(f"SSH Port:    {ssh_port}")
        if ssh_key:
            print(f"SSH Key:     {ssh_key}")
        print("="*60 + "\n")

        # Execute SSH command with file as stdin
        with open(str(source[0]), "rb") as f:
            result = subprocess.run(cmd, stdin=f, capture_output=False, text=False)

        if result.returncode != 0:
            raise exception.PlatformioException(
                f"SSH upload failed with exit code {result.returncode}"
            )

        print("\n" + "="*60)
        print("UPLOAD SUCCESSFUL")
        print("="*60 + "\n")

        # Post-upload execution if configured
        if env.GetProjectOption("upload_run_after", False):
            return self._run_remote_command(user, host, ssh_port, ssh_key, path, env)

        return 0

    def _run_remote_command(self, user, host, ssh_port, ssh_key, remote_path, env):
        """Run the uploaded program on the remote target."""
        cmd = ["ssh"]
        cmd.extend(["-p", str(ssh_port)])

        if ssh_key:
            cmd.extend(["-i", os.path.expanduser(ssh_key)])

        cmd.append(f"{user}@{host}")

        # Get custom run command or use default
        run_command = env.GetProjectOption("upload_run_command", None)
        if run_command:
            cmd.append(run_command)
        else:
            cmd.append(remote_path)

        print("\n" + "="*60)
        print("RUNNING REMOTE PROGRAM")
        print("="*60)
        print(f"Target: {user}@{host}")
        print(f"Command: {run_command if run_command else remote_path}")
        print("="*60 + "\n")

        # Execute remote command (interactive - shows output directly)
        result = subprocess.run(cmd)

        return result.returncode

    def configure_debug_session(self, debug_config):
        """
        Configure remote debugging session for ARM Linux targets.
        Supports GDB/gdbserver over SSH for remote debugging.
        """
        # Get board configuration
        board_config = self.board_config(debug_config.get("env_name"))
        target_arch = board_config.get("build.arch", "armv7")

        # Determine GDB executable based on architecture
        if target_arch == "aarch64":
            gdb_path = "aarch64-linux-gnu-gdb"
        else:
            gdb_path = "arm-linux-gnueabihf-gdb"

        # On native ARM, use system GDB
        if self._is_native():
            gdb_path = "gdb"

        # Get debug tool (default to gdbserver-ssh for remote debugging)
        debug_tool = debug_config.get("tool", "gdbserver-ssh")

        # Get upload configuration for SSH connection
        upload_port = debug_config.get("upload_port")
        ssh_port = debug_config.get("ssh_port", "22")
        ssh_key = debug_config.get("ssh_key")

        # Get remote program path
        prog_path = debug_config.get("prog_path", "/tmp/program")
        if upload_port and ":" in upload_port:
            # Extract path from upload_port if specified
            if "@" in upload_port:
                _, host_part = upload_port.split("@", 1)
            else:
                host_part = upload_port
            if ":" in host_part:
                _, prog_path = host_part.split(":", 1)

        # Build SSH connection string
        ssh_target = None
        if upload_port:
            if "@" in upload_port:
                user_host = upload_port.split(":")[0]
                ssh_target = user_host
            else:
                ssh_target = upload_port.split(":")[0]

        # Configure debug server based on tool
        if debug_tool == "gdbserver-ssh":
            # SSH-tunneled gdbserver
            if not ssh_target:
                raise exception.PlatformioException(
                    "debug_port or upload_port must be configured for SSH debugging.\n"
                    "Add to platformio.ini:\n"
                    "  debug_port = user@hostname\n"
                    "  or use existing upload_port configuration"
                )

            # Build SSH command for GDB remote target
            ssh_cmd_parts = ["ssh", "-T"]
            if ssh_port and ssh_port != "22":
                ssh_cmd_parts.extend(["-p", str(ssh_port)])
            if ssh_key:
                ssh_cmd_parts.extend(["-i", os.path.expanduser(ssh_key)])
            ssh_cmd_parts.append(ssh_target)
            ssh_cmd_parts.append("gdbserver - " + prog_path)

            ssh_cmd = " ".join(ssh_cmd_parts)

            debug_config["server_executable"] = None
            debug_config["server_arguments"] = []
            debug_config["port"] = f"| {ssh_cmd}"

        elif debug_tool == "gdb-remote":
            # Direct TCP connection to gdbserver (manual setup required)
            debug_port = debug_config.get("port", "localhost:2345")
            debug_config["port"] = debug_port

        # Set GDB executable
        debug_config["executable"] = gdb_path

        # Set program path for symbol loading
        debug_config["prog_path"] = prog_path

        # Add init commands
        init_cmds = []

        if debug_tool == "gdbserver-ssh":
            # For SSH tunneling, use extended-remote with pipe
            init_cmds.extend([
                f"target extended-remote {debug_config['port']}",
                f"set remote exec-file {prog_path}",
                "set sysroot /",
            ])
        else:
            # For direct TCP connection
            init_cmds.append(f"target extended-remote {debug_config['port']}")

        # Add custom init commands from config
        custom_init = debug_config.get("init_cmds", [])
        if custom_init:
            init_cmds.extend(custom_init)

        debug_config["init_cmds"] = init_cmds

        return debug_config

    def get_boards(self, id_=None):
        """
        Return board configurations.
        Overridden to add debug configuration to board definitions.
        """
        result = super().get_boards(id_)
        if not result:
            return result

        # Add debug tool support to all boards
        if id_:
            # Single board
            return self._add_debug_to_board(result)
        else:
            # All boards
            return {key: self._add_debug_to_board(value)
                    for key, value in result.items()}

    def _add_debug_to_board(self, board):
        """Add debug configuration to a board definition."""
        debug = board.manifest.get("debug", {})

        # Set default debug tools
        debug["tools"] = {
            "gdbserver-ssh": {
                "server": {
                    "package": None,
                    "executable": None,
                    "arguments": []
                },
                "init_cmds": [
                    "target extended-remote $DEBUG_PORT",
                    "set remote exec-file $PROG_PATH",
                    "set sysroot /"
                ],
                "extra_cmds": [
                    "break main",
                    "continue"
                ]
            },
            "gdb-remote": {
                "server": {
                    "package": None,
                    "executable": None,
                    "arguments": []
                },
                "init_cmds": [
                    "target extended-remote $DEBUG_PORT"
                ],
                "extra_cmds": [
                    "break main",
                    "continue"
                ]
            }
        }

        # Set default debug tool
        if "default" not in debug:
            debug["default"] = "gdbserver-ssh"

        board.manifest["debug"] = debug
        return board
