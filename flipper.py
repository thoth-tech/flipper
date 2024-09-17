#!/usr/bin/python3

import tomllib
import subprocess
import argparse
import os


args = None

# Relative to the home directory
GAMES_PATH = "Games"
SYSTEM_PATH = os.path.join(GAMES_PATH, "LaunchScripts")

CPP_FILES = "*.cpp"
CPP_LINK_SPLASHKIT = "-lSplashkit"


class Game:
    def __init__(self, config):
        config = tomllib.load(fp)

        self.meta = config["meta"]
        self.git = config["git"]
        self.es = config.get("emulationstation")

        self.cloned = False

    def clone(self):
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
        if not self.cloned:
            self.clone()

        build_path = os.path.join(GAMES_PATH, self.meta["name"], self.git.get("directory", ""))
        os.chdir(build_path)

        # Create a path to put the compiled binary
        os.makedirs(os.path.join(build_path, "bin"), exist_ok=True)

        cmd = []

        if self.meta["language"] == "cs":
            cmd += ["dotnet", "publish"]
            cmd += ["--configuration", "release"]
            cmd += ["--runtime", args.cs_runtime]
            cmd += ["-o", "bin"]

        elif self.meta["language"] == "cpp":
            cmd.append(args.cpp-prefix + args.cpp)
            cmd.append(CPP_FILES)
            cmd.append(CPP_LINK_SPLASHKIT)
            cmd += ["-o", "bin/" + self.meta["name"]]
        else:
            print(f"{self.meta['name']}: Unknown language {self.meta['language']}")

        print(f"Building {self.meta['name']}...")
        print(" ".join(cmd))
        subprocess.run(cmd)

    def generate_run_script(self):
        script = ""

        if self.meta["language"] == "cs" or self.meta["language"] == "cpp":
            script = f"""
            #!/bin/sh
            ~/{GAMES_PATH}/{self.meta['name']}/bin/{self.meta['name']}
            """
        else:
            print(f"{self.meta['name']}: Unknown language {self.meta['language']}")

        os.makedirs(SYSTEM_PATH, exist_ok=True)
        with open(os.path.join(SYSTEM_PATH, self.meta["name"] + ".sh"), "w+") as fp:
            fp.write(script)
            os.fchmod(fp, 0o755)

    def es_config(self):
        pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="splashkit arcade package manager")

    parser.add_argument("--cs-runtime", help="dotnet runtime architecture", default="linux-x64")
    parser.add_argument("--cpp-prefix", help="cpp compiler prefix", default="")
    parser.add_argument("--cpp", help="cpp compiler", default="cpp")
    parser.add_argument("--path", help="path to the games repo", default=os.curdir)

    args = parser.parse_args()

    games = []

    for file in os.listdir(args.path):
        if not file.endswith(".toml"):
            continue

        path = os.path.join(args.path, file)

        with open(path, "rb") as fp:
            games.append(Game(fp))

    for game in games:
        game.build()
        game.generate_run_script()
