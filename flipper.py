#!/usr/bin/python3

import argparse
import os
import subprocess
import textwrap
import tomllib
import xml.etree.ElementTree as xml

from datetime import datetime

ARCHIVE_NAME = f"splashkit-games-{datetime.now():%Y%m%d-%H%M%S}.tar.gz"

HOME_PATH = "~"
GAMES_PATH = "Games"  # relative to HOME_PATH
SYSTEM_PATH = os.path.join(GAMES_PATH, "LaunchScripts")

CPP_FILES = "*.cpp"
CPP_LINK_SPLASHKIT = "-lSplashkit"

args = None


class Game:
    def __init__(self, config):
        config = tomllib.load(fp)

        self.meta = config["meta"]
        self.git = config["git"]
        self.es = config.get("emulationstation", {})

        self.cloned = False

    def clone(self):
        """Clone the game's source code"""
        cmd = ["git", "clone"]
        cmd.append("--depth=1")

        if "branch" in self.git.keys():
            cmd += ["--branch", self.git["branch"]]

        cmd += [self.git["repo"], os.path.join(GAMES_PATH, self.meta["name"])]

        print(f"Cloning {self.meta['name']}...")
        print(" ".join(cmd))

        subprocess.run(cmd)
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
            cmd.append(args.cpp - prefix + args.cpp)
            cmd.append(CPP_FILES)
            cmd.append(CPP_LINK_SPLASHKIT)
            cmd += ["-o", "bin/" + self.meta["name"]]
        else:
            print(f"{self.meta['name']}: Unknown language {self.meta['language']}")

        print(f"Building {self.meta['name']}...")
        print(" ".join(cmd))

        old_path = os.getcwd()
        os.chdir(build_path)

        subprocess.run(cmd)

        os.chdir(old_path)

    def generate_run_script(self):
        """Generate a run script for the game"""
        script = ""

        if self.meta["language"] == "cs" or self.meta["language"] == "cpp":
            script = f"""\
            #!/bin/sh
            {os.path.join(HOME_PATH, GAMES_PATH, self.meta['name'], 'bin', self.meta['name'])}
            """
        else:
            print(f"{self.meta['name']}: Unknown language {self.meta['language']}")

        os.makedirs(SYSTEM_PATH, exist_ok=True)
        with open(os.path.join(SYSTEM_PATH, self.meta["name"] + ".sh"), "w+") as fp:
            fp.write(textwrap.dedent(script))
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

        if (description := self.meta.get("description")) is not None:
            desc = xml.SubElement(game, "desc")
            desc.text = description

        for tag, val in self.es.items():
            element = xml.SubElement(game, tag)
            element.text = str(val)


def create_archive():
    cmd = ["tar", "czvf", f"../{ARCHIVE_NAME}", "."]
    subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="splashkit arcade package manager")

    parser.add_argument(
        "--cs-runtime", help="dotnet runtime architecture", default="linux-x64"
    )
    parser.add_argument("--cpp-prefix", help="cpp compiler prefix", default="")
    parser.add_argument("--cpp", help="cpp compiler", default="cpp")
    parser.add_argument("--path", help="path to the games repo", default=os.curdir)

    args = parser.parse_args()

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
