import os
import time
import datetime
from utils import llm

class SystemCommands:
    def __init__(self, state):
        self.commands = {
            "nohup": self.command_nohup,
            # "useradd": self.command_useradd,
            # "usermod": self.command_usermod,
            # "userdel": self.command_userdel,
            # "groupadd": self.command_groupadd,
            "lscpu": self.command_lscpu,
            "dmesg": self.command_dmesg,
            "su": self.command_su,
            "systemctl": self.command_systemctl,
            "service": self.command_service,
            "jobs": self.command_jobs,
            "bg": self.command_bg,
            "fg": self.command_fg,
            "killall": self.command_killall,
            "strace": self.command_strace,
            "tmux": self.command_tmux,
            "watch": self.command_watch,
            "crontab": self.command_crontab,
            "at": self.command_at,
            "basename": self.command_basename,
            "dirname": self.command_dirname,
            "halt": self.command_halt,
        }
        self.state = state

    def command_top(self, command, client_ip):
        args = command[1:]  # Get command arguments
        user = self.state.get('user', 'root')
        hostname = self.state.get('hostname', 'localhost')
        current_time = time.strftime('%H:%M:%S')
        uptime_seconds = int(time.time() - self.state.get('start_time', time.time()))
        uptime_str = self.format_uptime(uptime_seconds)
        load_average = "0.00, 0.00, 0.00"

        # Handle help option
        if '--help' in args or '-h' in args:
            output = (
                "Usage:\n"
                "  top -hv | -bcHisS -d delay -n iterations -p pid [, pid ...]\n"
                "\n"
                "The traditional switches '-' and whitespace are optional.\n"
                "Example:  top - -d 1 -p 1\n"
            )
            return output

        # Simulate error for invalid options
        valid_options = {'-b', '-c', '-H', '-i', '-s', '-S', '-d', '-n', '-p', '--help', '-h', '-v'}
        for arg in args:
            if arg.startswith('-') and arg not in valid_options and not arg.startswith(('-d', '-n', '-p')):
                return f"top: unknown option '{arg}'\nTry 'top --help' for more information.\n"

        # Simulate iteration limit if '-n' option is used
        iterations = None
        if '-n' in args:
            try:
                n_index = args.index('-n') + 1
                iterations = int(args[n_index])
            except (ValueError, IndexError):
                return "top: option requires an argument -- 'n'\nTry 'top --help' for more information.\n"

        # Simulate delay between updates if '-d' option is used
        delay = 3.0  # Default delay in seconds
        if '-d' in args:
            try:
                d_index = args.index('-d') + 1
                delay = float(args[d_index])
            except (ValueError, IndexError):
                return "top: option requires an argument -- 'd'\nTry 'top --help' for more information.\n"

        # Simulate specific PIDs if '-p' option is used
        pids = []
        if '-p' in args:
            try:
                p_index = args.index('-p') + 1
                while p_index < len(args) and not args[p_index].startswith('-'):
                    pids.extend([int(pid.strip(',')) for pid in args[p_index].split(',')])
                    p_index += 1
                if not pids:
                    raise ValueError
            except (ValueError, IndexError):
                return "top: option '-p' requires an argument\nUsage: top -p pid [, pid ...]\n"

        # Prepare the output
        return llm.handle_with_llm("top", args, client_ip)

    def format_uptime(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            return f"{days} days, {hours:02d}:{minutes:02d}"
        elif hours > 0:
            return f"{hours:02d}:{minutes:02d}"
        else:
            return f"{minutes} min"


    def generate_process_list(self, pids):
        user = self.state.get('user', 'root')
        # Simulated process entries
        processes = [
            {
                "pid": 1,
                "user": "root",
                "pr": "20",
                "ni": "0",
                "virt": "225268",
                "res": "7088",
                "shr": "4096",
                "s": "S",
                "cpu": "0.0",
                "mem": "0.7",
                "time": "0:00.03",
                "command": "systemd"
            },
            {
                "pid": 2,
                "user": "root",
                "pr": "20",
                "ni": "0",
                "virt": "0",
                "res": "0",
                "shr": "0",
                "s": "S",
                "cpu": "0.0",
                "mem": "0.0",
                "time": "0:00.00",
                "command": "kthreadd"
            },
            {
                "pid": 3,
                "user": "root",
                "pr": "20",
                "ni": "0",
                "virt": "0",
                "res": "0",
                "shr": "0",
                "s": "S",
                "cpu": "0.0",
                "mem": "0.0",
                "time": "0:00.00",
                "command": "ksoftirqd/0"
            },
            {
                "pid": os.getpid(),
                "user": user,
                "pr": "20",
                "ni": "0",
                "virt": "100000",
                "res": "5000",
                "shr": "2000",
                "s": "R",
                "cpu": "0.0",
                "mem": "0.5",
                "time": "0:00.01",
                "command": "bash"
            },
        ]
        # Filter processes if specific PIDs are requested
        if pids:
            processes = [proc for proc in processes if proc["pid"] in pids]
            if not processes:
                return "No matching processes found.\n"
        # Build process list string
        process_list = ""
        return process_list

    def command_nohup(self, command, client_ip):
        args = command[1:]  # Get the arguments after 'nohup'

        # Check for help option or missing command
        if not args or '--help' in args or '-h' in args:
            if not args:
                return "nohup: missing operand\nTry 'nohup --help' for more information.\n"
            output = (
                "Usage: nohup COMMAND [ARG]...\n"
                "  or:  nohup OPTION\n"
                "Run COMMAND, ignoring hangup signals.\n\n"
                "      --help     display this help and exit\n"
                "      --version  output version information and exit\n"
                "\n"
                "If standard input is a terminal, redirect it from an unreadable file.\n"
                "If standard output is a terminal, append output to 'nohup.out' if possible,\n"
                "or '$HOME/nohup.out', or '/tmp/nohup.out' if neither of the first two are\n"
                "writable.\n"
                "If standard error is a terminal, redirect it to standard output.\n"
                "To save output to FILE, use 'nohup COMMAND > FILE'.\n"
                "\n"
                "NOTE: your shell may have its own version of nohup, which usually supersedes\n"
                "the version described here.  Please refer to your shell's documentation\n"
                "for details about the options it supports.\n"
            )
            return output

        # Handle version option
        if '--version' in args:
            output = "nohup (GNU coreutils) 8.30\n"
            return output

        # Simulate running the command
        cmd_to_run = args[0]
        cmd_args = args[1:]

        # Check if the command exists in the available commands
        available_commands = self.state.get('commands', {})
        if cmd_to_run not in available_commands:
            return f"nohup: failed to run command '{cmd_to_run}': No such file or directory\n"

        # Simulate ignoring input and appending output to 'nohup.out'
        output = "nohup: ignoring input and appending output to 'nohup.out'\n"

        # Simulate execution of the command
        simulated_command_output = f"Simulated execution of '{cmd_to_run}' with arguments {cmd_args}\n"
        output += simulated_command_output

        # Add the command to a simulated background job list
        bg_jobs = self.state.get('background_jobs', [])
        bg_jobs.append({
            'command': cmd_to_run,
            'args': cmd_args,
            'pid': len(bg_jobs) + 1,  # Simulate a PID
            'status': 'Running',
        })
        self.state['background_jobs'] = bg_jobs

        return llm.handle_with_llm("nohup", command, client_ip)

    def command_lscpu(self, command, client_ip):
        args = command[1:]  # Extract command arguments

        # Define valid options
        valid_options = {'-h', '--help', '-p', '--parse', '-J', '--json', '-x', '--hex'}

        # Check for help option or unknown options
        if '-h' in args or '--help' in args:
            return llm.handle_with_llm("lscpu", args, client_ip)

        # Handle unknown options
        for arg in args:
            if arg.startswith('-') and arg.split('=')[0] not in valid_options:
                return f"lscpu: unrecognized option '{arg}'\nTry 'lscpu --help' for more information.\n"

        # Handle JSON output format
        if '-J' in args or '--json' in args:
            output = {
                "architecture": "x86_64",
                "cpu_op_modes": ["32-bit", "64-bit"],
                "byte_order": "Little Endian",
                "cpu_count": 4,
                "online_cpu_list": "0-3",
                "threads_per_core": 2,
                "cores_per_socket": 2,
                "socket_count": 1,
                "numa_node_count": 1,
                "vendor_id": "GenuineIntel",
                "cpu_family": 6,
                "model": 158,
                "model_name": "Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz",
                "stepping": 10,
                "cpu_mhz": 1800.0,
                "bogomips": 3600.0,
                "virtualization": "VT-x",
                "caches": {
                    "L1d": "128K",
                    "L1i": "128K",
                    "L2": "1M",
                    "L3": "6M"
                },
                "numa_node_0_cpu_list": "0-3",
                "flags": [
                    "fpu", "vme", "de", "pse", "tsc", "msr", "pae", "mce", "cx8", "apic", "sep", "mtrr", "pge", "mca", "cmov",
                    "pat", "pse36", "clflush", "mmx", "fxsr", "sse", "sse2", "ss", "ht", "tm", "pbe", "syscall", "nx", "pdpe1gb",
                    "rdtscp", "lm", "constant_tsc", "arch_perfmon", "pebs", "bts", "rep_good", "nopl", "xtopology", "nonstop_tsc",
                    "cpuid", "pni", "pclmulqdq", "dtes64", "monitor", "ds_cpl", "vmx", "smx", "est", "tm2", "ssse3", "sdbg",
                    "fma", "cx16", "xtpr", "pdcm", "pcid", "dca", "sse4_1", "sse4_2", "x2apic", "movbe", "popcnt", "tsc_deadline_timer",
                    "aes", "xsave", "avx", "f16c", "rdrand", "hypervisor", "lahf_lm", "abm", "3dnowprefetch", "epb", "cat_l3",
                    "mba", "pti", "md_clear", "ibrs", "ibpb", "stibp", "ssbd", "vme"
                ]
            }
            return output  # JSON formatted dictionary

        # Handle parse option (returning specific fields)
        parse_fields = None
        for arg in args:
            if arg.startswith('-p') or arg.startswith('--parse'):
                try:
                    parse_fields = arg.split('=')[1].split(',')
                except IndexError:
                    return "lscpu: option '-p' requires an argument\nTry 'lscpu --help' for more information.\n"

        # Prepare simulated output
        # Place this within the simulated `cpu_info` dictionary
        cpu_info = {
            "Architecture": "x86_64",
            "CPU op-mode(s)": "32-bit, 64-bit",
            "Byte Order": "Little Endian",
            "CPU(s)": "8",
            "On-line CPU(s) list": "0-7",
            "Thread(s) per core": "2",
            "Core(s) per socket": "4",
            "Socket(s)": "1",
            "NUMA node(s)": "1",
            "Vendor ID": "GenuineIntel",
            "CPU family": "6",
            "Model": "158",
            "Model name": "Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz",
            "Stepping": "10",
            "CPU MHz": "1992.000",
            "BogoMIPS": "3984.00",
            "Virtualization": "VT-x",
            "L1d cache": "32K",
            "L1i cache": "32K",
            "L2 cache": "256K",
            "L3 cache": "8192K",
            "NUMA node0 CPU(s)": "0-7"
        }

        # Filter output based on parse fields
        if parse_fields:
            output = ""
            for field in parse_fields:
                if field in cpu_info:
                    output += f"{field}: {cpu_info[field]}\n"
                else:
                    output += f"{field}: field not found\n"
            return output

        # Default output (if no specific format or options requested)
        output = "\n".join([f"{key}: {value}" for key, value in cpu_info.items()]) + "\n"
        return llm.handle_with_llm("lscpu", args, client_ip)

    def command_dmesg(self, command, client_ip):
        args = command[1:]  # Get the arguments after 'dmesg'

        # Define supported options for simulation
        supported_options = {'-c', '--clear', '-h', '--help', '-s', '--buffer-size', '-T', '--ctime', '-D', '-E', '-n', '-r', '-f'}

        # Handle help option
        if '-h' in args or '--help' in args:
            output = (
                "Usage: dmesg [options]\n"
                "Print or control the kernel ring buffer.\n\n"
                "  -C, --clear              clear the ring buffer\n"
                "  -c, --read-clear         read and clear all messages\n"
                "  -D, --console-off        disable printing messages to console\n"
                "  -d, --show-delta         show time delta between printed messages\n"
                "  -E, --console-on         enable printing messages to console\n"
                "  -e, --reltime            show local time and time delta in human readable format\n"
                "  -H, --human              human readable output\n"
                "  -k, --kernel             print kernel messages\n"
                "  -L, --color[=WHEN]       colorize messages (auto, always or never)\n"
                "  -n, --level LEVEL        set console logging level\n"
                "  -r, --raw                print raw message buffer\n"
                "  -S, --syslog             force dmesg to use the syslog(2) kernel interface\n"
                "  -s, --buffer-size SIZE   use a buffer of SIZE\n"
                "  -T, --ctime              print human readable timestamps\n"
                "  -t, --notime             don't print timestamps\n"
                "  -u, --userspace          print userspace messages\n"
                "  -f, --facility FACILITY  restrict output to defined facilities\n"
                "  -l, --level LEVEL        restrict output to defined levels\n"
                "      --since TIME         show messages since TIME\n"
                "      --until TIME         show messages until TIME\n"
                "      --time-format FORMAT show timestamp using the given format\n"
                "      --timezone           show timestamps with timezones\n"
                "      --decode             decode facility and level to readable prefixes\n"
                "  -h, --help               display this help and exit\n"
                "  -V, --version            output version information and exit\n"
            )
            return output

        # Handle version option
        if '-V' in args or '--version' in args:
            output = "dmesg from util-linux 2.34\n"
            return output

        # Simulate clearing the ring buffer
        if '-C' in args or '--clear' in args:
            self.state['dmesg_buffer'] = []
            return ''

        # Simulate reading and clearing the ring buffer
        if '-c' in args or '--read-clear' in args:
            return llm.handle_with_llm("dmesg", args, client_ip)

        # Handle unsupported options
        for arg in args:
            if arg.startswith('-') and arg not in supported_options:
                return f"dmesg: invalid option -- '{arg}'\nTry 'dmesg --help' for more information.\n"

        # Simulate printing the kernel ring buffer
        buffer = self.state.get('dmesg_buffer', self.generate_dmesg_buffer())
        output = '\n'.join(buffer) + '\n'

        # Handle '-T' or '--ctime' option for human-readable timestamps
        if '-T' in args or '--ctime' in args:
            return llm.handle_with_llm("dmesg", args, client_ip)

        return llm.handle_with_llm("dmesg", args, client_ip)

    # def generate_dmesg_buffer(self):
    #     # Simulate the kernel ring buffer messages
    #     simulated_buffer = [
    #         "[    0.000000] Initializing cgroup subsys cpuset",
    #         "[    0.000000] Initializing cgroup subsys cpu",
    #         "[    0.000000] Initializing cgroup subsys cpuacct",
    #         "[    0.000000] Linux version 5.4.0-42-generic (buildd@lgw01-amd64-052) "
    #         "(gcc version 9.3.0 (Ubuntu 9.3.0-10ubuntu2)) #46-Ubuntu SMP "
    #         "Fri Jul 10 00:24:02 UTC 2020 (Ubuntu 5.4.0-42.46-generic 5.4.44)",
    #         "[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-5.4.0-42-generic root=UUID=xxxxxxx ro quiet splash",
    #         "[    0.000000] KERNEL supported cpus:",
    #         "[    0.000000]   Intel GenuineIntel",
    #         "[    0.000000]   AMD AuthenticAMD",
    #         "[    0.000000] x86/fpu: Supporting XSAVE feature 0x001: 'x87 floating point registers'",
    #         "[    0.000000] x86/fpu: Supporting XSAVE feature 0x002: 'SSE registers'",
    #         "[    0.000000] x86/fpu: Enabled xstate features 0x3, context size is 0x240 bytes, using 'standard' format.",
    #         "[    0.000000] BIOS-provided physical RAM map:",
    #         # ... more lines can be added to simulate a realistic dmesg output
    #     ]
    #     self.state['dmesg_buffer'] = simulated_buffer
    #     return simulated_buffer

    # def format_dmesg_with_timestamps(self, buffer):
    #     # Convert the timestamps to human-readable format
    #     formatted_buffer = []
    #     boot_time = self.state.get('boot_time', time.time() - 300)  # Assume the system booted 5 minutes ago
    #     for line in buffer:
    #         # Extract the timestamp from the line
    #         try:
    #             timestamp_str, message = line.split(']', 1)
    #             timestamp = float(timestamp_str.strip('[]'))
    #             message_time = boot_time + timestamp
    #             human_time = time.strftime('%a %b %d %H:%M:%S %Y', time.localtime(message_time))
    #             formatted_line = f"[{human_time}] {message.strip()}"
    #             formatted_buffer.append(formatted_line)
    #         except ValueError:
    #             # If parsing fails, include the line as is
    #             formatted_buffer.append(line)
    #     return '\n'.join(formatted_buffer) + '\n'

    def command_su(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "Password:\n"

        if '-c' in args:
            try:
                cmd = args[args.index('-c') + 1]
                return f"Executing '{cmd}' as superuser\n"
            except IndexError:
                return "su: option '-c' requires an argument\n"

        if '-s' in args:
            try:
                shell = args[args.index('-s') + 1]
                return f"Switching to shell '{shell}' for user\n"
            except IndexError:
                return "su: option '-s' requires an argument\n"

        return f"su: unrecognized option '{args[0]}'\nTry 'su --help' for more information.\n"

    def command_systemctl(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return (
                "systemctl [OPTIONS] COMMAND [ARGS...]\n\n"
                "To see available commands, run 'systemctl --help'.\n"
            )

        if 'start' in args or 'stop' in args or 'restart' in args:
            try:
                action = args[0]
                service = args[1]
                return f"systemctl: {action.capitalize()}ed {service}.service successfully\n"
            except IndexError:
                return f"systemctl: '{args[0]}' requires a service name\n"

        if 'status' in args:
            try:
                service = args[1]
                return (
                    f"{service}.service - {service.capitalize()} Service\n"
                    f"   Loaded: loaded (/etc/systemd/system/{service}.service; enabled)\n"
                    "   Active: active (running)\n"
                )
            except IndexError:
                return "systemctl: 'status' requires a service name\n"

        if '--version' in args:
            return "systemd 245 (245.4-4ubuntu3.2)\n"

        return "systemctl: unrecognized command\n"

    def command_service(self, command, client_ip):
        args = command[1:]

        if len(args) < 2:
            return "Usage: service SERVICE COMMAND\n"

        service_name = args[0]
        action = args[1]

        if action in ['start', 'stop', 'restart', 'status']:
            return f"Service '{service_name}' {action}ed\n"

        return f"service: unrecognized action '{action}'\n"

    def command_jobs(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "[1]   Running    sleep 60 &\n[2]   Stopped    vim file.txt\n"

        if '-l' in args:
            return "[1] 12345 Running    sleep 60 &\n[2] 23456 Stopped    vim file.txt\n"

        return "jobs: unknown option\n"

    def command_bg(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "bg: current: no such job\n"

        job_id = args[0].lstrip('%')
        return f"[{job_id}] Running in background\n"

    def command_fg(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "fg: current: no such job\n"

        job_id = args[0].lstrip('%')
        return f"[{job_id}] Brought to foreground\n"

    def command_killall(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return (
                "killall: usage: killall [-u user] [-q] [-w] [-eI] "
                "[-o|p|s|t|w|z] name...\n"
            )

        process_name = args[0]

        if '-q' in args:
            return f"killall: quiet mode enabled, killing '{process_name}' silently\n"

        return f"killall: '{process_name}' process terminated\n"

    def command_strace(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "strace: must have PROG [ARGS] or -p PID\n"

        if '-p' in args:
            try:
                pid = args[args.index('-p') + 1]
                return (
                    f"Attaching to process {pid}...\n"
                    "read(3, 0x7ffc0d28f8b0, 4096) = 1024\n"
                )
            except IndexError:
                return "strace: option requires an argument -- 'p'\n"

        program = args[0]
        return (
            f"strace: tracing calls for program '{program}'...\n"
            'open("/dev/null", O_RDONLY) = 3\n'
        )
    
    def command_tmux(self, command, client_ip):
        args = command[1:]
        
        if len(args) == 0:
            return (
                "usage: tmux [-2CluvV] [-c shell-command] [-f file] [-L socket-name] [-S socket-path]\n"
                "            [command [flags]]\n"
            )
        
        # Version display
        if '-V' in args or '--version' in args:
            return "tmux 3.1b\n"
        
        # Simulate session creation or attach
        if 'new-session' in args:
            session_index = args.index('new-session') + 1
            session_name = args[session_index] if len(args) > session_index else "default"
            return f"tmux: new session '{session_name}' created\n"
        elif 'attach-session' in args:
            session_index = args.index('attach-session') + 1
            session_name = args[session_index] if len(args) > session_index else "default"
            return f"tmux: attached to session '{session_name}'\n"
        elif '-L' in args:
            socket_index = args.index('-L') + 1
            socket_name = args[socket_index] if len(args) > socket_index else "default"
            return f"tmux: using socket '{socket_name}'\n"
        
        return "tmux: unknown command\nTry 'tmux -h' for help.\n"
    
    def command_watch(self, command, client_ip):
        args = command[1:]
        interval = 2  # default interval

        if '-n' in args:
            try:
                interval = int(args[args.index('-n') + 1])
            except (IndexError, ValueError):
                return "watch: invalid interval; must be a number\n"

        if '--differences' in args:
            cumulative = '=cumulative' if '--differences=cumulative' in args else ''
            return f"watching differences{cumulative} every {interval}s: {' '.join(args)}\n"

        if '-d' in args:
            return f"watching command for changes every {interval}s: {' '.join(args)}\n"

        return (
            f"Every {interval:.1f}s: {' '.join(args)}    "
            f"{time.strftime('%a %b %d %H:%M:%S %Y')}\n"
        )

    def command_crontab(self, command, client_ip):
        args = command[1:]
        
        if '-l' in args:
            return "*/5 * * * * /path/to/script.sh\n0 0 * * 1 /path/to/backup.sh\n"
        
        if '-e' in args:
            editor = os.getenv('EDITOR', 'nano')
            return f"crontab: editing crontab using {editor}\n"
        
        if '-r' in args:
            return "crontab: removing crontab for user\n"
    
        if '-u' in args:
            try:
                user = args[args.index('-u') + 1]
                return f"crontab for {user} listed\n"
            except IndexError:
                return "crontab: option requires an argument -- 'u'\n"
    
        return "crontab: usage error\nusage: crontab [-u user] file\n"

    def command_at(self, command, client_ip):
        args = command[1:]
        
        if len(args) == 0:
            return "at: usage: at [-V] [-q queue] [-f file] [-mldbv] TIME\n"
        
        if '-f' in args:
            try:
                file = args[args.index('-f') + 1]
                return f"at: executing job from file '{file}'\n"
            except IndexError:
                return "at: option '-f' requires an argument\n"
        
        # Time parsing
        try:
            schedule_time = args[0]
            datetime.datetime.strptime(schedule_time, "%H:%M")
            return f"Job scheduled at {schedule_time}\n"
        except ValueError:
            return "at: invalid time format\n"

    def command_basename(self, command, client_ip):
        args = command[1:]
        
        if len(args) == 0:
            return (
                "basename: missing operand\nTry 'basename --help' for more information.\n"
            )
        
        file_path = args[0]
        suffix = args[1] if len(args) > 1 else ''
        base_name = os.path.basename(file_path)
        if suffix and base_name.endswith(suffix):
            base_name = base_name[:-len(suffix)]
        return f"{base_name}\n"

    def command_dirname(self, command, client_ip):
        args = command[1:]
        
        if len(args) == 0:
            return (
                "dirname: missing operand\nTry 'dirname --help' for more information.\n"
            )
        
        file_path = args[0]
        dir_name = os.path.dirname(file_path)
        return f"{dir_name}\n"

    def command_halt(self, command, client_ip):
        args = command[1:]
    
        if '-f' in args or '--force' in args:
            return "halt: forcing system shutdown\n"
    
        if '-p' in args:
            return "halt: powering off system\n"
    
        if '-w' in args:
            return "halt: simulating shutdown\n"
        return "halt: system is going down\n"
    