import os
import time
import random
from utils import llm
import re


class PackageCommands:
    def __init__(self, state):
        self.commands = {
            "apt-get": self.command_aptget,
            "/usr/bin/vmstat": self.command_vmstat,
            "/usr/bin/uptime": self.command_uptime,
            "/bin/ps": self.command_ps,
            "/usr/bin/iostat": self.command_iostat,
            "/usr/bin/htop": self.command_htop,
            "/usr/bin/free": self.command_free,
            "/bin/df": self.command_df,
            "/usr/bin/top": self.command_top,
            "/usr/bin/sar": self.command_sar,
        }
        self.state = state  # Shared state containing 'cwd', 'filesystem', 'commands'

    def command_aptget(self, command, client_ip):
        args = command[1:]
        if len(args) == 0:
            return self.do_locked()

        if args[0] == 'install':
            return self.do_install(args)
        else:
            return self.do_locked()

    '''not really sure how i can fit in the llm command here'''

    def do_install(self, args):
        output = ""
        if len(args) <= 1:
            output += f"0 upgraded, 0 newly installed, 0 to remove and {random.randint(200,300)} not upgraded.\n"
            return output

        packages = {}
        for pkg_name in [re.sub('[^A-Za-z0-9]', '', x) for x in args[1:]]:
            packages[pkg_name] = {
                'version': f"{random.choice((0, 1))}.{random.randint(1, 40)}-{random.randint(1, 10)}",
                'size': random.randint(100, 900)
            }
        totalsize = sum(pkg['size'] for pkg in packages.values())

        output += "Reading package lists... Done\n"
        output += "Building dependency tree\n"
        output += "Reading state information... Done\n"
        output += "The following NEW packages will be installed:\n"
        output += "  " + ' '.join(packages.keys()) + "\n"
        output += f"0 upgraded, {len(packages)} newly installed, 0 to remove and 259 not upgraded.\n"
        output += f"Need to get {totalsize}.2kB of archives.\n"
        output += f"After this operation, {int(totalsize * 2.2)}kB of additional disk space will be used.\n"

        # Simulate package fetching and installation
        for i, pkg_name in enumerate(packages.keys(), start=1):
            pkg = packages[pkg_name]
            output += f"Get:{i} http://ftp.debian.org stable/main {pkg_name} {pkg['version']} [{pkg['size']}.2kB]\n"
            time.sleep(random.uniform(1, 2))
        output += f"Fetched {totalsize}.2kB in 1s (4493B/s)\n"
        output += "Reading package fields... Done\n"
        time.sleep(random.uniform(1, 2))
        output += "Reading package status... Done\n"
        output += "(Reading database ... 177887 files and directories currently installed.)\n"
        time.sleep(random.uniform(1, 2))
        for pkg_name in packages.keys(


        ):
            pkg = packages[pkg_name]
            output += f"Unpacking {pkg_name} (from .../archives/{pkg_name}_{pkg['version']}_i386.deb) ...\n"
            time.sleep(random.uniform(1, 2))
        output += "Processing triggers for man-db ...\n"
        time.sleep(2)
        for pkg_name in packages.keys():
            pkg = packages[pkg_name]
            output += f"Setting up {pkg_name} ({pkg['version']}) ...\n"
            # Simulate creating the executable in the filesystem
            self.state['filesystem'].mkfile(
                f"/usr/bin/{pkg_name}", uid=0, gid=0, size=random.randint(10000, 90000), mode=0o755)
            # Simulate the package executable outputting a segmentation fault when run
            self.state['commands'][pkg_name] = self.create_segmentation_fault_command(
                pkg_name)
            time.sleep(2)
        return output

    def do_locked(self):
        output = ""
        output += "E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)\n"
        output += "E: Unable to lock the list directory\n"
        return output

    def create_segmentation_fault_command(self, name):
        def command_segmentation_fault(command, client_ip):
            return f"{name}: Segmentation fault\n"
        return command_segmentation_fault

    def command_vmstat(self, command, client_ip):
        if not self.is_allow():
            return
        args = command[1:]
        return llm.handle_with_llm("vmstat", args, client_ip)

    def command_uptime(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate system uptime details
        uptime_hours = random.randint(1, 100)  # Simulating hours of uptime
        # Simulating number of logged-in users
        users = random.randint(1, 5)
        load_avg = [round(random.uniform(0, 1.5), 2)
                    for _ in range(3)]  # Simulating load averages

        # Format the time similar to what the uptime command would output
        current_time = time.strftime('%H:%M:%S')

        output = f" {current_time} up {uptime_hours} hours,  {users} user,  load average: {load_avg[0]}, {load_avg[1]}, {load_avg[2]}"
        return output

    def command_ps(self, command, client_ip):
        if not self.is_allow():
            return
        args = command[1:]
        return llm.handle_with_llm("ps", args, client_ip)

    def command_iostat(self, command, client_ip):
        if not self.is_allow():
            return
        args = command[1:]
        return llm.handle_with_llm("ps", args, client_ip)

    def command_htop(self, command, client_ip):
        if not self.is_allow():
            return
        args = command[1:]
        return llm.handle_with_llm("htop", args, client_ip)

    def command_free(self, command, client_ip):
        if not self.is_allow():
            return

        args = command[1:]
        return llm.handle_with_llm("free", args, client_ip)

    def command_df(self, command, client_ip):
        if not self.is_allow():
            return

        args = command[1:]
        return llm.handle_with_llm("df", args, client_ip)

    def command_top(self, command, client_ip):
        if not self.is_allow():
            return

        args = command[1:]
        return llm.handle_with_llm("top", args, client_ip)

    def command_sar(self, command, client_ip):
        if not self.is_allow():
            return

        args = command[1:]
        return llm.handle_with_llm("sar", args, client_ip)

    def is_allow(self):
        # Placeholder for permission check
        return True