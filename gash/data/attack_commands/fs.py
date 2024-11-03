# fs.py

import os
import time
import stat
import fnmatch
import hashlib
import random

# Constants for file attributes
A_NAME, A_TYPE, A_UID, A_GID, A_SIZE, A_MODE, A_CTIME, A_CONTENTS, A_TARGET, A_REALFILE = range(10)
T_FILE, T_DIR, T_LINK, T_BLK, T_CHR, T_SOCK, T_FIFO = range(7)

# Custom exceptions
class TooManyLevels(Exception):
    pass

class FileNotFound(Exception):
    pass

class HoneyPotFilesystem:
    def __init__(self, fs):
        self.fs = fs
        self.newcount = 0  # Keep count of new files to limit resource usage

    def resolve_path(self, path, cwd):
        pieces = path.rstrip('/').split('/')

        if path.startswith('/'):
            cwd_parts = []
        else:
            cwd_parts = [x for x in cwd.strip('/').split('/') if x]

        for piece in pieces:
            if piece == '..':
                if cwd_parts:
                    cwd_parts.pop()
                continue
            elif piece == '.' or not piece:
                continue
            else:
                cwd_parts.append(piece)

        return '/' + '/'.join(cwd_parts)

    def getfile(self, path):
        if path == '/':
            return self.fs
        pieces = path.strip('/').split('/')
        p = self.fs
        while pieces:
            piece = pieces.pop(0)
            found = False
            if p[A_TYPE] != T_DIR:
                return False
            for item in p[A_CONTENTS]:
                if item[A_NAME] == piece:
                    p = item
                    found = True
                    break
            if not found:
                return False
        return p

    def exists(self, path):
        return self.getfile(path) is not False

    def is_dir(self, path):
        file = self.getfile(path)
        return file and file[A_TYPE] == T_DIR

    def mkfile(self, path, uid, gid, size, mode, ctime=None):
        if self.newcount > 10000:
            return False
        if ctime is None:
            ctime = time.time()
        dir_path = os.path.dirname(path)
        dir_node = self.getfile(dir_path)
        if not dir_node or dir_node[A_TYPE] != T_DIR:
            return False
        filename = os.path.basename(path)
        # Remove existing file with the same name
        dir_node[A_CONTENTS] = [f for f in dir_node[A_CONTENTS] if f[A_NAME] != filename]
        dir_node[A_CONTENTS].append([
            filename, T_FILE, uid, gid, size, mode, ctime, [], None, None
        ])
        self.newcount += 1
        return True

    def mkdir(self, path, uid, gid, size, mode, ctime=None):
        if self.newcount > 10000:
            return False
        if ctime is None:
            ctime = time.time()
        dir_path = os.path.dirname(path)
        dir_node = self.getfile(dir_path)
        if not dir_node or dir_node[A_TYPE] != T_DIR:
            return False
        dirname = os.path.basename(path)
        # Remove existing directory with the same name
        dir_node[A_CONTENTS] = [d for d in dir_node[A_CONTENTS] if d[A_NAME] != dirname]
        dir_node[A_CONTENTS].append([
            dirname, T_DIR, uid, gid, size, mode, ctime, [], None, None
        ])
        self.newcount += 1
        return True

    def file_contents(self, path, count=0):
        if count > 10:
            raise TooManyLevels("Too many levels of symbolic links")
        file = self.getfile(path)
        if not file:
            raise FileNotFound(f"No such file: '{path}'")
        if file[A_TYPE] == T_LINK:
            return self.file_contents(file[A_TARGET], count + 1)
        elif file[A_TYPE] == T_FILE:
            return f"Contents of {file[A_NAME]}\n"
        else:
            raise FileNotFound(f"Cannot read contents of '{path}'")

class FileSystemCommands:
    def __init__(self, filesystem, cwd):
        self.commands = {
            "ls": self.command_ls,
            "cd": self.command_cd,
            "mkdir": self.command_mkdir,
            "rmdir": self.command_rmdir,
            "touch": self.command_touch,
            "cp": self.command_cp,
            "mv": self.command_mv,
            "rm": self.command_rm,
            "find": self.command_find,
            "cat": self.command_cat,
            "head": self.command_head,
            "tail": self.command_tail,
            "chmod": self.command_chmod,
            "chown": self.command_chown,
        }

        self.filesystem = filesystem
        self.cwd = cwd  # Current working directory

    # Helper methods
    def get_permissions(self, mode, file_type):
        perms = ['-'] * 10
        if file_type == T_DIR:
            perms[0] = 'd'
        elif file_type == T_LINK:
            perms[0] = 'l'
        # User permissions
        perms[1] = 'r' if mode & stat.S_IRUSR else '-'
        perms[2] = 'w' if mode & stat.S_IWUSR else '-'
        perms[3] = 'x' if mode & stat.S_IXUSR else '-'
        # Group permissions
        perms[4] = 'r' if mode & stat.S_IRGRP else '-'
        perms[5] = 'w' if mode & stat.S_IWGRP else '-'
        perms[6] = 'x' if mode & stat.S_IXGRP else '-'
        # Other permissions
        perms[7] = 'r' if mode & stat.S_IROTH else '-'
        perms[8] = 'w' if mode & stat.S_IWOTH else '-'
        perms[9] = 'x' if mode & stat.S_IXOTH else '-'
        return ''.join(perms)

    def uid2name(self, uid):
        return 'root' if uid == 0 else f'user{uid}'

    def gid2name(self, gid):
        return 'root' if gid == 0 else f'group{gid}'

    # Command implementations
    def command_ls(self, command, client_ip):
        args = command[1:]
        paths = []
        show_all = False
        detailed = False

        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'l' in arg:
                    detailed = True
            else:
                paths.append(arg)

        if not paths:
            paths.append(self.cwd)

        output = []
        for path in paths:
            resolved_path = self.filesystem.resolve_path(path, self.cwd)
            file_node = self.filesystem.getfile(resolved_path)
            if not file_node:
                output.append(f"ls: cannot access '{path}': No such file or directory")
                continue

            if file_node[A_TYPE] == T_DIR:
                dir_contents = file_node[A_CONTENTS]
                if detailed:
                    output.append(self.format_detailed_list(dir_contents, show_all))
                else:
                    output.append(self.format_simple_list(dir_contents, show_all))
            else:
                if detailed:
                    output.append(self.format_detailed_list([file_node], show_all))
                else:
                    output.append(file_node[A_NAME])

        return "\n".join(output) + "\n"

    def format_simple_list(self, files, show_all):
        names = []
        for item in files:
            name = item[A_NAME]
            if not show_all and name.startswith('.'):
                continue
            if item[A_TYPE] == T_DIR:
                name += '/'
            elif item[A_TYPE] == T_LINK:
                name += '@'
            names.append(name)
        return "  ".join(names)

    def format_detailed_list(self, files, show_all):
        output = []
        total_blocks = 0
        for item in files:
            if not show_all and item[A_NAME].startswith('.'):
                continue
            total_blocks += (item[A_SIZE] + 511) // 512

        output.append(f"total {total_blocks}")
        for item in files:
            if not show_all and item[A_NAME].startswith('.'):
                continue
            perms = self.get_permissions(item[A_MODE], item[A_TYPE])
            links = 1  # For simplicity, using 1 as link count
            owner = self.uid2name(item[A_UID])
            group = self.gid2name(item[A_GID])
            size = item[A_SIZE]
            mtime = time.strftime('%b %d %H:%M', time.localtime(item[A_CTIME]))
            name = item[A_NAME]
            if item[A_TYPE] == T_LINK:
                target = item[A_TARGET]
                name += f" -> {target}"
            output.append(f"{perms} {links} {owner} {group} {size} {mtime} {name}")
        return "\n".join(output)

    def command_cd(self, command, client_ip):
        if len(command) < 2:
            self.cwd = "/home"
        else:
            path = self.filesystem.resolve_path(command[1], self.cwd)
            if self.filesystem.is_dir(path):
                self.cwd = path
            else:
                return f"bash: cd: {command[1]}: No such file or directory\n"
        return ""

    def command_mkdir(self, command, client_ip):
        if len(command) < 2:
            return "mkdir: missing operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        success = self.filesystem.mkdir(path, uid=0, gid=0, size=4096, mode=0o755)
        if success:
            return ""
        else:
            return f"mkdir: cannot create directory '{command[1]}': Permission denied\n"

    def command_rmdir(self, command, client_ip):
        if len(command) < 2:
            return "rmdir: missing operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        dir_node = self.filesystem.getfile(path)
        if not dir_node or dir_node[A_TYPE] != T_DIR:
            return f"rmdir: failed to remove '{command[1]}': No such directory\n"
        if dir_node[A_CONTENTS]:
            return f"rmdir: failed to remove '{command[1]}': Directory not empty\n"
        # Remove the directory
        parent_path = os.path.dirname(path)
        parent_dir = self.filesystem.getfile(parent_path)
        parent_dir[A_CONTENTS] = [d for d in parent_dir[A_CONTENTS] if d[A_NAME] != os.path.basename(path)]
        return ""

    def command_touch(self, command, client_ip):
        if len(command) < 2:
            return "touch: missing file operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        success = self.filesystem.mkfile(path, uid=0, gid=0, size=0, mode=0o644)
        if success:
            return ""
        else:
            return f"touch: cannot touch '{command[1]}': Permission denied\n"

    def command_cp(self, command, client_ip):
        if len(command) < 3:
            return "cp: missing file operand\n"
        src = self.filesystem.resolve_path(command[1], self.cwd)
        dst = self.filesystem.resolve_path(command[2], self.cwd)
        src_file = self.filesystem.getfile(src)
        if not src_file or src_file[A_TYPE] != T_FILE:
            return f"cp: cannot stat '{command[1]}': No such file or directory\n"
        # Copy the file
        success = self.filesystem.mkfile(dst, src_file[A_UID], src_file[A_GID], src_file[A_SIZE], src_file[A_MODE])
        if success:
            return ""
        else:
            return f"cp: cannot create regular file '{command[2]}': Permission denied\n"

    def command_mv(self, command, client_ip):
        if len(command) < 3:
            return "mv: missing file operand\n"
        src = self.filesystem.resolve_path(command[1], self.cwd)
        dst = self.filesystem.resolve_path(command[2], self.cwd)
        src_file = self.filesystem.getfile(src)
        if not src_file:
            return f"mv: cannot stat '{command[1]}': No such file or directory\n"
        # Remove src from parent directory
        src_parent_path = os.path.dirname(src)
        src_parent = self.filesystem.getfile(src_parent_path)
        src_parent[A_CONTENTS] = [f for f in src_parent[A_CONTENTS] if f[A_NAME] != os.path.basename(src)]
        # Update name and add to destination directory
        src_file[A_NAME] = os.path.basename(dst)
        dst_parent_path = os.path.dirname(dst)
        dst_parent = self.filesystem.getfile(dst_parent_path)
        if not dst_parent or dst_parent[A_TYPE] != T_DIR:
            return f"mv: cannot move '{command[1]}': No such directory '{dst_parent_path}'\n"
        dst_parent[A_CONTENTS].append(src_file)
        return ""

    def command_rm(self, command, client_ip):
        if len(command) < 2:
            return "rm: missing operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        file_node = self.filesystem.getfile(path)
        if not file_node:
            return f"rm: cannot remove '{command[1]}': No such file or directory\n"
        if file_node[A_TYPE] == T_DIR:
            return f"rm: cannot remove '{command[1]}': Is a directory\n"
        # Remove file from parent directory
        parent_path = os.path.dirname(path)
        parent = self.filesystem.getfile(parent_path)
        parent[A_CONTENTS] = [f for f in parent[A_CONTENTS] if f[A_NAME] != os.path.basename(path)]
        return ""

    def command_find(self, command, client_ip):
        path = self.cwd if len(command) < 2 else self.filesystem.resolve_path(command[1], self.cwd)
        matches = []
        def recursive_find(current_path, node):
            name = node[A_NAME]
            full_path = os.path.join(current_path, name)
            matches.append(full_path)
            if node[A_TYPE] == T_DIR:
                for item in node[A_CONTENTS]:
                    recursive_find(full_path, item)
        file_node = self.filesystem.getfile(path)
        if not file_node:
            return f"find: `{path}`: No such file or directory\n"
        recursive_find(os.path.dirname(path), file_node)
        return "\n".join(matches) + "\n"

    def command_cat(self, command, client_ip):
        if len(command) < 2:
            return "cat: missing file operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        try:
            content = self.filesystem.file_contents(path)
            return content
        except FileNotFound:
            return f"cat: {command[1]}: No such file or directory\n"
        except TooManyLevels:
            return f"cat: {command[1]}: Too many levels of symbolic links\n"

    def command_head(self, command, client_ip):
        if len(command) < 2:
            return "head: missing file operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        try:
            content = self.filesystem.file_contents(path)
            lines = content.splitlines()[:10]
            return "\n".join(lines) + "\n"
        except FileNotFound:
            return f"head: cannot open '{command[1]}' for reading: No such file or directory\n"
        except TooManyLevels:
            return f"head: {command[1]}: Too many levels of symbolic links\n"

    def command_tail(self, command, client_ip):
        if len(command) < 2:
            return "tail: missing file operand\n"
        path = self.filesystem.resolve_path(command[1], self.cwd)
        try:
            content = self.filesystem.file_contents(path)
            lines = content.splitlines()[-10:]
            return "\n".join(lines) + "\n"
        except FileNotFound:
            return f"tail: cannot open '{command[1]}' for reading: No such file or directory\n"
        except TooManyLevels:
            return f"tail: {command[1]}: Too many levels of symbolic links\n"

    def command_chmod(self, command, client_ip):
        if len(command) < 3:
            return "chmod: missing operand\n"
        mode_str = command[1]
        path = self.filesystem.resolve_path(command[2], self.cwd)
        file_node = self.filesystem.getfile(path)
        if not file_node:
            return f"chmod: cannot access '{command[2]}': No such file or directory\n"
        try:
            mode = int(mode_str, 8)
            file_node[A_MODE] = mode
            return ""
        except ValueError:
            return f"chmod: invalid mode: '{mode_str}'\n"

    def command_chown(self, command, client_ip):
        if len(command) < 3:
            return "chown: missing operand\n"
        owner = command[1]
        path = self.filesystem.resolve_path(command[2], self.cwd)
        file_node = self.filesystem.getfile(path)
        if not file_node:
            return f"chown: cannot access '{command[2]}': No such file or directory\n"
        # For simplicity, assume owner is 'root' or 'user1000'
        if owner == 'root':
            file_node[A_UID] = 0
        elif owner.startswith('user'):
            try:
                uid = int(owner[4:])
                file_node[A_UID] = uid
            except ValueError:
                return f"chown: invalid user: '{owner}'\n"
        else:
            return f"chown: invalid user: '{owner}'\n"
        return ""

    # Add any additional command methods here

# Example usage:
if __name__ == "__main__":
    # Initialize filesystem structure
    fs_structure = [
        '/', T_DIR, 0, 0, 4096, 0o755, time.time(), [
            ['home', T_DIR, 0, 0, 4096, 0o755, time.time(), [
                ['user', T_DIR, 1000, 1000, 4096, 0o755, time.time(), [], None, None],
            ], None, None],
            ['etc', T_DIR, 0, 0, 4096, 0o755, time.time(), [
                ['passwd', T_FILE, 0, 0, 1024, 0o644, time.time(), [], None, None],
            ], None, None],
            ['var', T_DIR, 0, 0, 4096, 0o755, time.time(), [], None, None],
            ['tmp', T_DIR, 0, 0, 4096, 0o777, time.time(), [], None, None],
        ], None, None
    ]

    filesystem = HoneyPotFilesystem(fs_structure)
    cwd = "/"

    # Instantiate the FileSystemCommands with the filesystem and current working directory
    fs_commands = FileSystemCommands(filesystem, cwd)

    # Example command execution
    client_ip = "127.0.0.1"
    response = fs_commands.command_ls(['ls', '-l'], client_ip)
    print(response)