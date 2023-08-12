#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Script for cleaning / building all examples, with the option to skip some of them
#

import os
from pathlib import Path
import platform
import shutil
import sys


class CXX:

    def __init__(self):
        self.command = shutil.which("cxx")
        if not self.command:
            print("error: cxx must exist in PATH")
            sys.exit(1)
        self.directory = None

    def set_directory(self, directory):
        self.directory = str(directory)

    def run(self, args, dummy=False, verbose=True):
        """The first argument is the command given to cxx. If the first argument contains a ':'
        it is interpreted as being a list of commands to run cxx with. For example "fastclean:build"
        will first run "cxx fastclean" and then "cxx build"."""
        # Trim all arguments, and remove the empty ones
        args = [arg.strip() for arg in args if arg.strip()]
        if self.directory:
            cmd = f"{self.command} -C {self.directory} " + " ".join(args)
        else:
            cmd = f"{self.command} " + " ".join(args)
        if dummy or verbose:
            print(cmd)
        if dummy:
            return
        if os.system(cmd) != 0:
            print(f"ERROR: {cmd}", file=sys.stderr)
            sys.exit(1)

    def version(self):
        self.run(["version"])


class Figlet:

    def __init__(self):
        self.command = shutil.which("figlet")

    def msg(self, message):
        if self.command:
            print()
            os.system(f"{self.command} -f small {message}")
            print()
        else:
            print('|\n|\n|  ' + message + '...\n|\n|')


def run_all(f, cxx, command, exampledir, skiplist, dummyrun=False):
    if command == "build":
        f.msg("Building all examples")
    elif command in ["clean", "fastclean"]:
        f.msg("Cleaning all examples")
    elif command == "rebuild":
        f.msg("Rebuilding all examples")
    elif command == "run":
        f.msg("Running all examples")

    for projectdir in exampledir.iterdir():
        if projectdir.is_dir():
            projectname = os.path.basename(projectdir)

            # informative output
            print("\n------- " + projectdir.name + " -------", flush=True)

            # skip, if needed
            if projectname in skiplist:
                if command not in ["clean", "fastclean"]:
                    print(f"Skipping {projectname} at {command}", flush=True)
                continue

            # special cases
            extraflag = ""
            if projectname == "sfml" and platform.system() == "Darwin":
                extraflag = "clang=1"

            # set the directory
            reldir = os.path.relpath(projectdir, Path.cwd())
            cxx.set_directory(reldir)

            # run the command. Empty arguments are ignored
            cxx.run([command, extraflag], dummy=dummyrun, verbose=True)
            sys.stdout.flush()


def main():
    # the first argument is a command, the rest are projects names to be skipped
    # possible commands: clean fastclean build run rebuild. All commands supported by cxx is ok.

    default_commands = ["fastclean", "build"]
    default_skiplist = ["boson"]

    args = sys.argv[1:]
    if len(args) < 1:
        command = ":".join(default_commands)
        skiplist = default_skiplist
    else:
        command = args[0] or ":".join(default_commands)
        skiplist = args[1:] or default_skiplist

    # directory of this source file
    thisdir = Path(os.path.realpath(__file__)).parent

    # ../examples
    exampledir = Path(thisdir.parent.joinpath('examples'))

    cxx = CXX()
    cxx.version()

    f = Figlet()

    if ":" in command:
        for cmd in command.split(":"):
            run_all(f, cxx, cmd, exampledir, skiplist, dummyrun=False)
    else:
        run_all(f, cxx, command, exampledir, skiplist, dummyrun=False)

    print("Done.", flush=True)


if __name__ == "__main__":
    main()
