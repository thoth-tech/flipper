#!/usr/bin/python3

import logging
import argparse
import os
import subprocess
import textwrap
import tomllib
import xml.etree.ElementTree as xml

from datetime import datetime

ARCHIVE_PATH = f"../splashkit-games-{datetime.now():%Y%m%d-%H%M%S}.tar.gz"

HOME_PATH = "~"
GAMES_PATH = "Games"  # relative to HOME_PATH
SYSTEM_PATH = os.path.join(GAMES_PATH, "LaunchScripts")

CPP_LINK_SPLASHKIT = "-lSplashKit"

# The verbose flag sets this to None so that stdout will be shown on stdout
STDOUT = subprocess.DEVNULL

# The verbose flag sets this to logging.DEBUG
LOG_LEVEL = logging.INFO

args = None
log = logging.getLogger("flipper")


class Game:
    def __init__(self, config):
        config = tomllib.load(fp)

        self.meta = config["meta"]
        self.git = config["git"]
        self.es = config.get("emulationstation", {})

        self.log = logging.getLogger(self.meta["name"])
        self.cloned = False

    def clone(self):
        """Clone the game's source code"""
        cmd = ["git", "clone"]
        cmd.append("--depth=1")

        if "branch" in self.git.keys():
            cmd += ["--branch", self.git["branch"]]

        cmd += [self.git["repo"], os.path.join(GAMES_PATH, self.meta["name"])]

        self.log.info(f"Cloning {self.meta['name']}...")
        self.log.debug(" ".join(cmd))

        subprocess.run(cmd, stdout=STDOUT)
        self.cloned = True

    def build(self):
        """Build the game

        For C++ and C# this creates a bin directory inside the cloned source
        containing the final executable
        """
        if not self.cloned:
            self.clone()

        build_path = os.path.join(
            GAMES_PATH, self.meta["name"], self.git.get("directory", "")
        )

        # Create a path to put the compiled binary
        os.makedirs(os.path.join(build_path, "bin"), exist_ok=True)

        cmd = []

        if self.meta["language"] == "cs":
            cmd += ["dotnet", "publish"]
            cmd += ["--configuration", "release"]
            cmd += ["--runtime", args.cs_runtime]
            cmd += ["-o", "bin"]
        elif self.meta["language"] == "cpp":
            cmd.append(args.cpp_prefix + args.cpp)
            cmd += [
                source for source in os.listdir(build_path) if source.endswith(".cpp")
            ]
            cmd.append(CPP_LINK_SPLASHKIT)
            cmd += ["-o", "bin/" + self.meta["name"]]
        else:
            self.log.critical(
                f"Unable to build, unknown language {self.meta['language']}"
            )
            exit(1)

        self.log.info(f"Building {self.meta['name']}...")
        self.log.debug(" ".join(cmd))

        subprocess.run(cmd, cwd=build_path, stdout=STDOUT)

    def generate_run_script(self):
        script_path = os.path.join(SYSTEM_PATH, self.meta["name"] + ".sh")
        self.log.info(f"Creating run script for {self.meta['name']} at {script_path}")

        """Generate a run script for the game"""
        script = ""

        if self.meta["language"] == "cs" or self.meta["language"] == "cpp":
            script = f"""\
            #!/bin/sh
            {os.path.join(HOME_PATH, GAMES_PATH, self.meta['name'], self.git.get('directory', ''), 'bin', self.meta['name'])}
            """
        else:
            self.log.error(
                f"Unable to create run script, unknown language {self.meta['language']}"
            )

        os.makedirs(SYSTEM_PATH, exist_ok=True)

        script = textwrap.dedent(script)
        self.log.debug(script)

        with open(script_path, "w+") as fp:
            fp.write(script)
            os.chmod(fp.name, 0o755)

    def es_config(self, gamelist):
        """Append the game's emulation station configuration

        This assumes that the gameList root tag already exist in the given
        element tree

        See https://github.com/thoth-tech/ArcadeMenu/blob/master/GAMELISTS.md
        for the file format
        """
        game = xml.SubElement(gamelist, "game")

        path = xml.SubElement(game, "path")
        path.text = os.path.join(HOME_PATH, SYSTEM_PATH, self.meta["name"] + ".sh")

        name = xml.SubElement(game, "name")
        name.text = self.meta["name"]

        self.log.info(f"Generating gamelist configuration for {self.meta['name']}")

        if (description := self.meta.get("description")) is not None:
            self.log.debug("Adding description tag")
            desc = xml.SubElement(game, "desc")
            desc.text = description
        else:
            self.log.warning("Game doesn't have a description")

        if (image := self.es.get("image")) is not None:
            self.log.debug("Adding image tag")
            desc = xml.SubElement(game, "image")
            desc.text = os.path.join(self.git.get("directory", ""), image)
        else:
            self.log.warning("Game doesn't have title image")

        for tag, val in self.es.items():
            if tag == "image":
                continue

            self.log.debug(f"Adding {tag} tag")
            element = xml.SubElement(game, tag)
            element.text = str(val)


def create_archive():
    log.info(f"Creating {ARCHIVE_PATH}")
    cmd = ["tar", "czvf", ARCHIVE_PATH, "."]
    log.debug(" ".join(cmd))
    subprocess.run(cmd, stdout=STDOUT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="splashkit arcade package manager")

    parser.add_argument(
        "--cs-runtime", help="dotnet runtime architecture", default="linux-x64"
    )
    parser.add_argument("--cpp-prefix", help="cpp compiler prefix", default="")
    parser.add_argument("--cpp", help="cpp compiler", default="g++")
    parser.add_argument("--path", help="path to the games repo", default=os.curdir)
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )

    args = parser.parse_args()

    if args.verbose:
        LOG_LEVEL = logging.DEBUG
        STDOUT = None

    logging.basicConfig(level=LOG_LEVEL)

    games = []

    for file in os.listdir(args.path):
        if not file.endswith(".toml"):
            continue

        with open(os.path.join(args.path, file), "rb") as fp:
            games.append(Game(fp))

    for game in games:
        game.build()

    for game in games:
        game.generate_run_script()

    gamelist = xml.Element("gameList")
    for game in games:
        game.es_config(gamelist)

    with open(os.path.join(SYSTEM_PATH, "gamelist.xml"), "wb+") as fp:
        tree = xml.ElementTree(gamelist)
        xml.indent(tree)
        tree.write(fp)

    create_archive()
