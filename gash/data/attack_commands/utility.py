# utility.py

import os
import time
import datetime

class UtilityCommands:
    def __init__(self, state):
        self.commands = {
            "whoami": self.command_whoami,
            "uptime": self.command_uptime,
            "w": self.command_w,
            "who": self.command_who,
            "echo": self.command_echo,
            "exit": self.command_exit,
            "logout": self.command_exit,
            "clear": self.command_clear,
            "hostname": self.command_hostname,
            "uname": self.command_uname,
            "ps": self.command_ps,
            "id": self.command_id,
            "passwd": self.command_passwd,
            "shutdown": self.command_shutdown,
            "reboot": self.command_reboot,
            "history": self.command_history,
            "date": self.command_date,
            "yes": self.command_yes,
            "chmod": self.command_nop,
            "set": self.command_nop,
            "unset": self.command_nop,
            "export": self.command_nop,
            "bash": self.command_nop,
            "sh": self.command_nop,
            "kill": self.command_nop,
            "su": self.command_nop,
            
        }
        self.state = state  # Shared state containing 'cwd', 'filesystem', 'user', etc.

    def command_whoami(self, command, client_ip):
        user = self.state.get('user', 'root')
        return f"{user}\n"

    def command_uptime(self, command, client_ip):
        current_time = time.time()
        start_time = self.state.get('start_time', current_time)
        uptime_seconds = int(current_time - start_time)
        uptime_str = self.format_uptime(uptime_seconds)
        current_time_str = time.strftime('%H:%M:%S')
        return f" {current_time_str} up {uptime_str},  1 user,  load average: 0.00, 0.00, 0.00\n"

    def format_uptime(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days !=1 else ''}")
        if hours > 0:
            parts.append(f"{hours}:{minutes:02d}")
        else:
            parts.append(f"{minutes} min")
        return ', '.join(parts)

    def command_w(self, command, client_ip):
        current_time = time.time()
        start_time = self.state.get('start_time', current_time)
        uptime_seconds = int(current_time - start_time)
        uptime_str = self.format_uptime(uptime_seconds)
        current_time_str = time.strftime('%H:%M:%S')
        output = f" {current_time_str} up {uptime_str},  1 user,  load average: 0.00, 0.00, 0.00\n"
        output += "USER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT\n"
        user = self.state.get('user', 'root')
        login_time = self.state.get('login_time', start_time)
        login_time_str = time.strftime('%H:%M', time.localtime(login_time))
        ip_address = client_ip[:17].ljust(17)
        output += f"{user.ljust(8)} pts/0    {ip_address} {login_time_str}    0.00s  0.00s  0.00s w\n"
        return output

    def command_who(self, command, client_ip):
        user = self.state.get('user', 'root')
        login_time = self.state.get('login_time', time.time())
        login_time_str = time.strftime('%b %d %H:%M', time.localtime(login_time))
        ip_address = client_ip
        output = f"{user}     pts/0        {ip_address}     {login_time_str}\n"
        return output

    def command_echo(self, command, client_ip):
        args = command[1:]
        return ' '.join(args) + '\n'

    def command_exit(self, command, client_ip):
        # Indicate that the session should be closed
        self.state['exit'] = True  # Set a flag in state to indicate exit
        return ''

    def command_clear(self, command, client_ip):
        # ANSI escape code to clear the screen
        return '\033[2J\033[H'

    def command_hostname(self, command, client_ip):
        hostname = self.state.get('hostname', 'localhost')
        return f"{hostname}\n"

    def command_uname(self, command, client_ip):
        args = command[1:]
        hostname = self.state.get('hostname', 'localhost')
        if len(args) and args[0].strip() == '-a':
            return f"Linux {hostname} 2.6.26-2-686 #1 SMP Wed Nov 4 20:45:37 UTC 2009 i686 GNU/Linux\n"
        else:
            return "Linux\n"

    def command_ps(self, command, client_ip):
        args = command[1:]
        user = self.state.get('user', 'root')
        args_flags = ''.join(args)
        output_lines = []
        output_lines.append("PID TTY          TIME CMD")
        output_lines.append("  1 ?        00:00:00 init")
        output_lines.append("  2 ?        00:00:00 kthreadd")
        output_lines.append("  3 ?        00:00:00 ksoftirqd/0")
        output_lines.append("  4 ?        00:00:00 kworker/0:0")
        output_lines.append("  5 ?        00:00:00 kworker/0:0H")
        output_lines.append(f" {os.getpid()} pts/0    00:00:00 bash")
        output_lines.append(f" {os.getpid()+1} pts/0    00:00:00 ps")
        return '\n'.join(output_lines) + '\n'

    def command_id(self, command, client_ip):
        user = self.state.get('user', 'root')
        uid = self.state.get('uid', 0)
        gid = self.state.get('gid', 0)
        return f"uid={uid}({user}) gid={gid}({user}) groups={gid}({user})\n"

    def command_passwd(self, command, client_ip):
        # Simulate password change failure due to authentication error
        output = (
            "Changing password for user.\n"
            "passwd: Authentication token manipulation error\n"
            "passwd: password unchanged\n"
        )
        return output

    def command_shutdown(self, command, client_ip):
        args = command[1:]
        if '--help' in args:
            output = (
                "Usage:     shutdown [-akrhHPfnc] [-t secs] time [warning message]",
                "-a:      use /etc/shutdown.allow",
                "-k:      don't really shutdown, only warn.",
                "-r:      reboot after shutdown.",
                "-h:      halt after shutdown.",
                "-P:      halt action is to turn off power.",
                "-H:      halt action is to just halt.",
                "-f:      do a 'fast' reboot (skip fsck).",
                "-F:      Force fsck on reboot.",
                "-n:      do not go through \"init\" but go down real fast.",
                "-c:      cancel a running shutdown.",
                "-t secs: delay between warning and kill signal.",
                "** the \"time\" argument is mandatory! (try \"now\") **",
            )
            return '\n'.join(output) + '\n'
        else:
            # Simulate the shutdown message
            hostname = self.state.get('hostname', 'localhost')
            current_time_str = time.ctime()
            output = (
                f"\nBroadcast message from root@{hostname} (pts/0) ({current_time_str}):\n",
                "\nThe system is going down for maintenance NOW!\n"
            )
            # Optionally, set a flag to indicate the session should be closed
            self.state['shutdown'] = True
            return '\n'.join(output)

    def command_reboot(self, command, client_ip):
        # Simulate the reboot message
        hostname = self.state.get('hostname', 'localhost')
        current_time_str = time.ctime()
        output = (
            f"\nBroadcast message from root@{hostname} (pts/0) ({current_time_str}):\n",
            "\nThe system is going down for reboot NOW!\n"
        )
        # Optionally, set a flag to indicate the session should be closed
        self.state['reboot'] = True
        return '\n'.join(output)

    def command_history(self, command, client_ip):
        args = command[1:]
        if '-c' in args:
            self.state['history'] = []
            return ''
        history = self.state.get('history', [])
        output = ''
        for i, cmd in enumerate(history, start=1):
            output += f' {i}  {cmd}\n'
        return output

    def command_date(self, command, client_ip):
        current_time = datetime.datetime.utcnow()
        return current_time.strftime("%a %b %d %H:%M:%S UTC %Y\n")

    def command_yes(self, command, client_ip):
        # Simulate 'yes' command outputting 'y' repeatedly
        return ('y\n' * 100)

    def command_nop(self, command, client_ip):
        # No operation command; does nothing
        return ''
    
    def command_grep(self, command, client_ip):
        args = command[1:]
        if not args:
            return "Usage: grep [OPTION]... PATTERN [FILE]...\n"
        pattern = args[0]
        files = args[1:]
        output = ""
        if files:
            for filename in files:
                output += f"{filename}: simulated matching lines for pattern '{pattern}'\n"
        else:
            output += f"simulated matching lines for pattern '{pattern}'\n"
        return output
    
    def command_awk(self, command, client_ip):
        args = command[1:]
        if not args:
            return "Usage: awk [OPTION]... 'program' [FILE]...\n"
        program = args[0]
        files = args[1:]
        output = ""
        if files:
            for filename in files:
                output += f"Simulated output of awk program '{program}' on file '{filename}'\n"
        else:
            output += f"Simulated output of awk program '{program}' on stdin\n"
        return output
    
    def command_whoami(self, command, client_ip):
        user = self.state.get('user', 'root')
        return f"{user}\n"

    def command_uptime(self, command, client_ip):
        current_time = time.time()
        start_time = self.state.get('start_time', current_time)
        uptime_seconds = int(current_time - start_time)
        uptime_str = self.format_uptime(uptime_seconds)
        current_time_str = time.strftime('%H:%M:%S')
        return f" {current_time_str} up {uptime_str},  1 user,  load average: 0.00, 0.00, 0.00\n"
    
    def format_uptime(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days !=1 else ''}")
        if hours > 0:
            parts.append(f"{hours}:{minutes:02d}")
        else:
            parts.append(f"{minutes} min")
        return ', '.join(parts)