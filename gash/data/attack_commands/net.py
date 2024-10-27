import time
import random
import re
import os  # Added import for os module
import hashlib
try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse  # Python 2


class NetworkCommands:
    def __init__(self, filesystem, cwd):
        self.commands = {
            "ping": self.command_ping,
            "curl": self.command_curl,
            "wget": self.command_wget,
            "tar": self.command_tar,
            "ifconfig": self.command_ifconfig,
            "ipaddr": self.command_ipaddr,
            "netstat": self.command_netstat,
            "ss": self.command_ss,
            "nc": self.command_nc,
            "traceroute": self.command_traceroute,
            "dig": self.command_dig,
            "nslookup": self.command_nslookup,
            "iptables": self.command_iptables,
            "ip": self.command_ip,
            "scp": self.command_scp,
            "rsync": self.command_rsync,
            "sftp": self.command_sftp,
            "ssh": self.command_ssh,
            "tcpdump": self.command_tcpdump,
            "watch": self.command_watch,
            "nmap": self.command_nmap,
            "who": self.command_who,
            "ssh-keygen": self.command_ssh_keygen,
            "ssh-agent": self.command_ssh_agent,
            "sshd": self.command_sshd,
            "ssh-copy-id": self.command_ssh_copy_id,
            "ssh-add": self.command_ssh_add,
        }

        self.filesystem = filesystem
        self.cwd = cwd

    def command_curl(self, command, client_ip):
        args = command[1:]
        url = None
        for arg in args:
            if not arg.startswith('-'):
                url = arg.strip()
                break

        if not url:
            return "curl: try 'curl --help' or 'curl --manual' for more information\n"

        # Validate the URL
        if not re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url):
            return f"curl: (6) Could not resolve host: {url}\n"

        # Simulate fetching the URL
        response = f"Fetching URL: {url}\n"
        # Simulate a delay
        time.sleep(1)

        # Simulate the response content
        response += "HTTP/1.1 200 OK\n"
        response += "Content-Type: text/html; charset=UTF-8\n"
        response += "Content-Length: 1234\n\n"
        response += f"<html><body><h1>Mocked response for {url}</h1></body></html>\n"
        return response

    def command_wget(self, command, client_ip):
        url = None
        for arg in command[1:]:
            if arg.startswith('-'):
                continue
            url = arg.strip()
            break

        if not url:
            return "wget: missing URL\nUsage: wget [OPTION]... [URL]...\nTry 'wget --help' for more options.\n"

        if '://' not in url:
            url = 'http://%s' % url

        urldata = urlparse(url)
        outfile = urldata.path.split('/')[-1] or 'index.html'
        limit_size = 0

        # Generate a safe output filename
        safeoutfile = '/tmp/%s_%s' % (
            time.strftime('%Y%m%d%H%M%S'),
            re.sub('[^A-Za-z0-9]', '_', url))

        # Simulate the download
        download_result = self.download(url, outfile, safeoutfile)
        if "Unsupported scheme" in download_result or "SSL not supported" in download_result:
            return download_result

        # Simulate saving the file in the virtual filesystem
        path = self.filesystem.resolve_path(outfile, self.cwd)
        success = self.filesystem.mkfile(
            path, uid=0, gid=0, size=0, mode=0o644)
        if not success:
            return f"wget: cannot write to '{outfile}' (Permission denied).\n"

        # Simulate successful download
        return download_result + self.success()

    def download(self, url, fakeoutfile, outputfile, *args, **kwargs):
        try:
            urldata = urlparse(url)
            scheme = urldata.scheme
            host = urldata.hostname
            port = urldata.port or (443 if scheme == 'https' else 80)
            path = urldata.path or '/'

            if scheme == 'https':
                return "Sorry, SSL not supported in this release\n"
            elif scheme != 'http':
                return f"{url}: Unsupported scheme.\n"
        except Exception as e:
            return f"{url}: Invalid URL.\n"

        # Simulate the download output
        output = f"--{time.strftime('%Y-%m-%d %H:%M:%S')}--  {url}\n"
        output += f"Resolving {host}... {random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}\n"
        output += f"Connecting to {host}:{port}... connected.\n"
        output += f"HTTP request sent, awaiting response... 200 OK\n"
        output += f"Length: unspecified [text/html]\n"
        output += f"Saving to: '{fakeoutfile}'\n\n"
        output += f"     0K                                                       0.00 B/s\n\n"
        output += f"{time.strftime('%Y-%m-%d %H:%M:%S')} (0.00 B/s) - '{fakeoutfile}' saved [0]\n"
        return output

    def success(self):
        return "Download completed successfully.\n"

    def error(self, error, url):
        return f"Error while downloading {url}: {error}\n"

    def command_tar(self, command, client_ip):
        args = command[1:]
        if len(args) < 2:
            return (
                "tar: You must specify one of the `-Acdtrux' options\n"
                "Try `tar --help' or `tar --usage' for more information.\n"
            )

        options = args[0]
        filename = args[1]

        extract = 'x' in options
        verbose = 'v' in options

        # Resolve the path to the tar file
        path = self.filesystem.resolve_path(filename, self.cwd)
        if not path or not self.filesystem.exists(path):
            return (
                f"tar: {filename}: Cannot open: No such file or directory\n"
                "tar: Error is not recoverable: exiting now\n"
                "tar: Child returned status 2\n"
                "tar: Error exit delayed from previous errors\n"
            )

        # Get the file node
        file_node = self.filesystem.getfile(path)
        if not file_node:
            return (
                "tar: This does not look like a tar archive\n"
                "tar: Skipping to next header\n"
                "tar: Error exit delayed from previous errors\n"
            )

        # Simulate extraction (since we can't read real files)
        # For demonstration, let's assume the tar contains a file 'file.txt'
        output = ""
        if extract:
            extracted_files = ['file.txt', 'dir1/', 'dir1/file2.txt']
            for item in extracted_files:
                dest_path = self.filesystem.resolve_path(
                    item.strip('/'), self.cwd
                )
                if verbose:
                    output += f"{item}\n"
                if item.endswith('/'):
                    # It's a directory
                    self.filesystem.mkdir(
                        dest_path, uid=0, gid=0, size=4096, mode=0o755
                    )
                else:
                    # It's a file
                    self.mkfullpath(os.path.dirname(dest_path), None)
                    self.filesystem.mkfile(
                        dest_path, uid=0, gid=0, size=1024, mode=0o644
                    )
        else:
            # If not extracting, list the contents
            output += "file.txt\ndir1/\ndir1/file2.txt\n"

        return output

    def mkfullpath(self, path, member):
        parts = path.strip('/').split('/')
        current_path = ''
        for part in parts:
            current_path += f"/{part}"
            if not self.filesystem.exists(current_path):
                self.filesystem.mkdir(
                    current_path, uid=0, gid=0, size=4096, mode=0o755
                )

    def command_ping(self, command, client_ip):
        args = command[1:]
        host = None

        for arg in args:
            if not arg.startswith('-'):
                host = arg.strip()
                break

        if not host:
            usage = [
                'Usage: ping [-LRUbdfnqrvVaA] [-c count] [-i interval] [-w deadline]',
                '            [-p pattern] [-s packetsize] [-t ttl] [-I interface or address]',
                '            [-M mtu discovery hint] [-S sndbuf]',
                '            [ -T timestamp option ] [ -Q tos ] [hop1 ...] destination',
            ]
            return "\n".join(usage) + "\n"

        # Simulate resolving the IP or generating a fake one based on the hostname
        if re.match(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', host):
            ip = host
        else:
            s = hashlib.md5(host.encode()).hexdigest()
            ip = '.'.join([str(int(s[i:i+2], 16)) for i in range(0, 8, 2)])

        # Simulate ping response output
        response = f"PING {host} ({ip}) 56(84) bytes of data.\n"

        # Simulate multiple replies
        for seq in range(1, 5):  # Simulate 4 pings (can be modified based on -c argument)
            time.sleep(1)  # Simulate time delay between pings
            ms = 40 + random.random() * 10
            response += f"64 bytes from {ip}: icmp_seq={seq} ttl=50 time={ms:.1f} ms\n"

        # Simulate ping statistics
        response += f"\n--- {host} ping statistics ---\n"
        response += f"4 packets transmitted, 4 received, 0% packet loss, time {random.randint(800, 1000)}ms\n"
        response += "rtt min/avg/max/mdev = 40.264/50.352/52.441/2.100 ms\n"

        return response

    def command_ifconfig(self, command, client_ip):

        args = command[1:]

        if len(args) == 0:
            # Simulate output for the default 'ifconfig' command without arguments
            output = "eth0      Link encap:Ethernet  HWaddr 00:0a:95:9d:68:16  \n"
            output += "          inet addr:192.168.0.101  Bcast:192.168.0.255  Mask:255.255.255.0\n"
            output += "          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1\n"
            output += "          RX packets:12345 errors:0 dropped:0 overruns:0 frame:0\n"
            output += "          TX packets:6789 errors:0 dropped:0 overruns:0 carrier:0\n"
            output += "          collisions:0 txqueuelen:1000\n"
            output += "          RX bytes:10485760 (10.4 MB)  TX bytes:5242880 (5.2 MB)\n"
            return output

        # Handle invalid or unknown interface
        interface = args[0]
        if interface != "eth0":
            return f"ifconfig: {interface}: error fetching interface information: Device not found\n"

        # Custom interface output
        return f"{interface}      Link encap:Ethernet  HWaddr 00:0a:95:9d:68:16\n"

    def command_ipaddr(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "ip: can't parse '': unknown command\n"

        if args[0] == "show":
            return "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN \n" \
                "    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n" \
                "    inet 127.0.0.1/8 scope host lo\n" \
                "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP \n" \
                "    link/ether 00:0a:95:9d:68:16 brd ff:ff:ff:ff:ff:ff\n" \
                "    inet 192.168.0.101/24 brd 192.168.0.255 scope global eth0\n"

        return f"ip: '{args[0]}' is an unknown command\n"
    
    def command_nc(self, command, client_ip):
        args = command[1:]

        if len(args) < 2:
            return "nc: missing destination or port\n"

        host = args[0]
        port = args[1]

        if not port.isdigit():
            return f"nc: port number invalid: {port}\n"

        # Simulate a connection attempt
        return f"Trying {host}...\nConnected to {host}.\nEscape character is '^]'.\n"
    
    def command_traceroute(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "Usage: traceroute [-46dFITnreAV] [-f first_ttl] [-m max_ttl] [-p port] [-q nqueries] [-N squeries] [-t tos] [-w waittime]\n" \
                "                 [-z sendwait] [-g gateway] [-i device] [-l flow_label] [-s source_addr] [-S] [-M method] [-O mod_options]\n" \
                "                 [-P proto] [--sport=port] [--dport=port] [-UL] [--firsthop=hop] [--mtu] host [packetlen]\n"

        host = args[0]
        return f"traceroute to {host} (192.168.0.1), 30 hops max, 60 byte packets\n" \
            " 1  192.168.0.1  1.123 ms  1.234 ms  1.456 ms\n" \
            " 2  10.0.0.1     10.456 ms  10.789 ms  11.001 ms\n"
            
    def command_dig(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "dig: usage: dig [@server] [domain] [query-type] [query-class] {options}\n"

        domain = args[0]
        if not re.match(r'^[\w.-]+\.[a-z]{2,}$', domain):
            return f"dig: '{domain}' is not a valid domain\n"

        # Simulate dig output
        return f"; <<>> DiG 9.10.6 <<>> {domain}\n" \
            f";;; global options: +cmd\n" \
            f";; Got answer:\n" \
            f";; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345\n" \
            f";; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0\n" \
            f";\n;; QUESTION SECTION:\n" \
            f";{domain}.                    IN      A\n" \
            f"\n;; ANSWER SECTION:\n" \
            f"{domain}.             300     IN      A       192.168.0.101\n" \
            f"\n;; Query time: 2 msec\n;; SERVER: 192.168.0.1#53(192.168.0.1)\n" \
            f";; WHEN: {time.strftime('%a %b %d %H:%M:%S %Y')}\n;; MSG SIZE  rcvd: 55\n"
    
    def command_nslookup(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "nslookup: usage: nslookup [OPTION]... [HOST] [SERVER]\n"

        host = args[0]
        if not re.match(r'^[\w.-]+\.[a-z]{2,}$', host):
            return f"nslookup: '{host}' is not a valid domain\n"

        # Simulate nslookup output
        return f"Server:         192.168.0.1\n" \
            f"Address:        192.168.0.1#53\n\n" \
            f"Non-authoritative answer:\n" \
            f"Name:   {host}\n" \
            f"Address: 192.168.0.101\n"
    
    def command_ip(self, command, client_ip):
        args = command[1:]

        if len(args) == 0 or args[0] not in ['addr', 'link', 'route']:
            return "ip: can't parse '': unknown command\n"

        if args[0] == 'addr':
            return "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n" \
                "    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n" \
                "    inet 127.0.0.1/8 scope host lo\n" \
                "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000\n" \
                "    link/ether 00:0a:95:9d:68:16 brd ff:ff:ff:ff:ff:ff\n" \
                "    inet 192.168.0.101/24 brd 192.168.0.255 scope global eth0\n"

        if args[0] == 'route':
            return "default via 192.168.0.1 dev eth0\n" \
                "192.168.0.0/24 dev eth0 proto kernel scope link src 192.168.0.101\n"

        return "ip: invalid command '{}'\n".format(args[0])
    
    def command_scp(self, command, client_ip):
        args = command[1:]
        
        if len(args) < 2:
            return "usage: scp [-346CDEFGILpqRrv] [-B bind_address] [-b batchfile] [-c cipher]\n" \
                "           [-i identity_file] [-l limit] [-o option] [-P port]\n" \
                "           [-S program] [[user@]host1:]file1 ... [[user@]host2:]file2\n"
        
        # Simulate SCP output
        source = args[0]
        destination = args[1]
        
        # Simulate success or permission denied error
        if "root" in destination:
            return f"scp: {destination}: Permission denied\n"
        
        return f"{source} -> {destination} (copied successfully)\n"
    
    def command_sftp(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "usage: sftp [-46aCfpqrv] [-B buffer_size] [-b batchfile] [-c cipher] [-D sftp_server_path]\n" \
                "            [-F ssh_config] [-i identity_file] [-l limit] [-o ssh_option] [-P port] [-R num_requests]\n" \
                "            [-S program] [-s subsystem | sftp_server] host\n"

        host = args[-1]

        return f"Connecting to {host}...\nsftp> "
    
    def command_ssh(self, command, client_ip):
        args = command[1:]

        if len(args) < 1:
            return "usage: ssh [-46AaCfGgKkMNnqsTtVvXxYy] [-b bind_address] [-c cipher_spec] [-D [bind_address:]port]\n" \
                "           [-E log_file] [-e escape_char] [-F configfile] [-I pkcs11] [-i identity_file]\n" \
                "           [-J destination] [-L address] [-l login_name] [-m mac_spec] [-O ctl_cmd]\n" \
                "           [-o option] [-p port] [-Q query_option] [-R address] [-S ctl_path]\n" \
                "           [-W host:port] [-w local_tun[:remote_tun]] destination [command]\n"

        host = args[0]

        return f"Trying {host}...\nConnected to {host}.\nLast login: {time.strftime('%a %b %d %H:%M:%S %Y')}\n"
    
    def command_tcpdump(self, command, client_ip):
        args = command[1:]

        if '-i' not in args:
            return "tcpdump: no suitable device found\n"

        interface = args[args.index('-i') + 1] if len(args) > 1 else None
        if not interface:
            return "tcpdump: failed to parse interface\n"

        return f"tcpdump: listening on {interface}, link-type EN10MB (Ethernet), capture size 262144 bytes\n"
    
    def command_watch(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "Usage: watch [-dhvt] [-n <seconds>] [--differences[=cumulative]] [command]\n"

        return f"Every 2.0s: {' '.join(args)}    {time.strftime('%a %b %d %H:%M:%S %Y')}\n"
    
    def command_nmap(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "Nmap 7.80 ( https://nmap.org )\nUsage: nmap [Scan Type(s)] [Options] {target specification}\n"

        target = args[-1]
        return f"Starting Nmap 7.80 ( https://nmap.org ) at {time.strftime('%a %b %d %H:%M:%S %Y')}\n" \
            f"Nmap scan report for {target} (192.168.0.101)\n" \
            "Host is up (0.0031s latency).\n" \
            "Not shown: 996 closed ports\n" \
            "PORT    STATE SERVICE\n22/tcp  open  ssh\n80/tcp  open  http\n443/tcp open  https\n"
            
    def command_who(self, command, client_ip):
        return f"{client_ip}    pts/0        {time.strftime('%b %d %H:%M')} (:0)\n"
    
    def command_ssh_keygen(self, command, client_ip):
        args = command[1:]

        if '-t' not in args:
            return "usage: ssh-keygen [-q] [-b bits] [-t type] [-N new_passphrase] [-C comment] [-f output_keyfile]\n"

        key_type = args[args.index('-t') + 1] if len(args) > 1 else None
        if not key_type:
            return "ssh-keygen: No type specified.\n"

        return f"Generating public/private {key_type} key pair.\nYour identification has been saved.\nYour public key has been saved.\n"
    
    def command_ssh_agent(self, command, client_ip):
        return "Agent pid 12345\n"
    
    def command_sshd(self, command, client_ip):
        args = command[1:]

        if '-t' in args:
            return "sshd: /etc/ssh/sshd_config line 23: Deprecated option RSAAuthentication\n"

        return "sshd: no hostkeys available -- exiting\n"
    
    def command_ssh_copy_id(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "Usage: ssh-copy-id [-i [identity_file]] [-o <ssh_options>] [user@]hostname\n"

        host = args[-1]
        return f"/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter {host}\n"
    
    def command_ssh_add(self, command, client_ip):
        args = command[1:]

        if len(args) == 0:
            return "The agent has no identities.\n"

        identity_file = args[0]
        return f"Identity added: {identity_file} (RSA)\n"