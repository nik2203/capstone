import os
import time
import random
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
        for pkg_name in packages.keys():
            pkg = packages[pkg_name]
            output += f"Unpacking {pkg_name} (from .../archives/{pkg_name}_{pkg['version']}_i386.deb) ...\n"
            time.sleep(random.uniform(1, 2))
        output += "Processing triggers for man-db ...\n"
        time.sleep(2)
        for pkg_name in packages.keys():
            pkg = packages[pkg_name]
            output += f"Setting up {pkg_name} ({pkg['version']}) ...\n"
            # Simulate creating the executable in the filesystem
            self.state['filesystem'].mkfile(f"/usr/bin/{pkg_name}", uid=0, gid=0, size=random.randint(10000, 90000), mode=0o755)
            # Simulate the package executable outputting a segmentation fault when run
            self.state['commands'][pkg_name] = self.create_segmentation_fault_command(pkg_name)
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

        # Simulate the 'vmstat' command output
        output = ""
        output += "procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu----\n"
        output += " r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st\n"
        output += " 1  0   2052 948836 3019968 12345632    0    0    12    34  105   290  2  1 97  0  0\n"
        output += " 0  1   2048 943128 3021456 12345984    0    0    11    33  108   320  1  0 98  0  0\n"
        return output

    def command_uptime(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate system uptime details
        uptime_hours = random.randint(1, 100)  # Simulating hours of uptime
        users = random.randint(1, 5)           # Simulating number of logged-in users
        load_avg = [round(random.uniform(0, 1.5), 2) for _ in range(3)]  # Simulating load averages
        
        # Format the time similar to what the uptime command would output
        current_time = time.strftime('%H:%M:%S')
        
        output = f" {current_time} up {uptime_hours} hours,  {users} user,  load average: {load_avg[0]}, {load_avg[1]}, {load_avg[2]}"
        return output

    def command_ps(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate the output of the 'ps' command, showing a list of processes
        output = ""
        output += "  PID TTY          TIME CMD\n"
        output += "    1 pts/0    00:00:00 bash\n"
        output += "   10 pts/0    00:00:00 ps\n"
        output += "   42 pts/0    00:00:00 sshd\n"
        output += "  101 pts/0    00:00:00 python3\n"
        output += "  202 pts/0    00:00:00 top\n"
        return output

    def command_iostat(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate the header of the 'iostat' command output
        output = ""
        output += "Linux 5.11.0-37-generic (honeypot)    10/18/2024      _x86_64_        (4 CPU)\n"
        output += "\n"
        output += "avg-cpu:  %user   %nice %system %iowait  %steal   %idle\n"
        output += "           0.58    0.00    0.11    0.04    0.00   99.27\n"
        output += "\n"
        
        # Simulate device statistics
        output += "Device            tps    kB_read/s    kB_wrtn/s    kB_read    kB_wrtn\n"
        output += "sda              1.12        12.34        22.11    1256112    2401123\n"
        output += "sdb              0.24         5.67         3.45     123456      65432\n"
        return output

    def command_htop(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate the 'htop' command output
        output = ""
        output += "htop: error: terminal is too small\n"
        output += "resize the terminal and try again\n"
        return output

    def command_free(self, command, client_ip):
        if not self.is_allow():
            return
        
        # Simulate the output of the 'free' command
        output = ""
        output += "              total        used        free      shared  buff/cache   available\n"
        output += "Mem:       16301064     12345632       948836        1436      3019968     3542976\n"
        output += "Swap:       2097148        2052     2095096\n"
        return output

    def command_df(self, command, client_ip):
        if not self.is_allow():
            return
        
        # Simulate the output of the 'df' command
        output = ""
        output += "Filesystem     1K-blocks     Used Available Use% Mounted on\n"
        output += "/dev/sda1       30421160  15069452  13846136  53% /\n"
        output += "tmpfs            8047520        72   8047448   1% /dev/shm\n"
        output += "tmpfs            8047520      1436   8046084   1% /run\n"
        output += "/dev/sdb1       12021120   1041234   10578886  10% /mnt/storage\n"
        return output

    def command_top(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate the header of the 'top' command output
        output = ""
        output += "top - 16:29:22 up 12 days,  3:11,  1 user,  load average: 0.58, 0.49, 0.52\n"
        output += "Tasks: 113 total,   1 running, 112 sleeping,   0 stopped,   0 zombie\n"
        output += "%Cpu(s):  2.3 us,  0.3 sy,  0.0 ni, 97.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st\n"
        output += "KiB Mem :  16301064 total,   948836 free,  12345632 used,  3019968 buff/cache\n"
        output += "KiB Swap:  2097148 total,  2095096 free,     2052 used.  3542976 avail Mem\n"

        # Simulate a few processes
        output += "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND\n"
        output += "    1 root      20   0   12536    968    752 S   0.0  0.0   0:01.25 init\n"
        output += "  123 root      20   0  142348   6056   3652 S   0.0  0.1   0:03.34 sshd\n"
        output += "  456 user      20   0  255820  12456   4520 S   0.3  0.2   1:12.45 python3\n"
        output += "  789 user      20   0  162784  50236  19208 S   0.7  1.3   0:23.67 top\n"
        output += " 1001 user      20   0  184984  24456   8544 R   0.7  0.5   0:04.12 bash\n"

        # Random chance of displaying a simulated load increase (just for fun)
        if random.choice([True, False]):
            output += "\n\nWarning: System load is increasing, monitor processes closely!"

        return output

    def command_sar(self, command, client_ip):
        if not self.is_allow():
            return

        # Simulate the 'sar' command output (for CPU utilization)
        output = ""
        output += "Linux 5.11.0-37-generic (honeypot)    10/18/2024      _x86_64_        (4 CPU)\n"
        output += "\n"
        output += "12:00:01 AM       CPU     %user     %nice   %system   %iowait    %steal     %idle\n"
        output += "12:10:01 AM       all      1.23      0.00      0.45      0.03      0.00     98.29\n"
        output += "12:20:01 AM       all      0.89      0.00      0.52      0.04      0.00     98.55\n"
        output += "12:30:01 AM       all      0.97      0.00      0.48      0.02      0.00     98.53\n"
        output += "12:40:01 AM       all      1.15      0.00      0.41      0.03      0.00     98.41\n"
        return output

    def is_allow(self):
        # Placeholder for permission check
        return True