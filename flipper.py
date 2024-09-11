import tomllib
import subprocess
import argparse
import os


args = None

CPP_FILES = "*.cpp"
CPP_LINK_SPLASHKIT = "-lSplashkit"


class Game:
    def __init__(self, fp):
        config = tomllib.load(fp)

        self.meta = config["meta"]
        self.git = config["git"]
        self.es = config["emulationstation"]

        self.cloned = False

    def clone(self):
        cmd = ["git", "clone"]
        cmd.append("--depth=1")

        if "branch" in git.keys():
            cmd += ["--branch", git["tag"]]

        cmd += [self.git["repo"], self.meta["name"]]

        print(f"Cloning {self.meta['name']}...")
        print("-" + " ".join(cmd))

        subprocess.run(cmd)
        self.cloned = True
       
    def build(self):
        if not self.cloned:
            self.clone()

        os.chdir(self.meta["name"])

        if self.meta["language"] == "cs":
            cmd += ["dotnet", "build", "--arch", args["cs-arch"]]

        elif self.meta["language"] == "cpp":
            cmd.append(args["cpp-prefix"] + args["cpp"])
            cmd.append(CPP_FILES)
            cmd.append(CPP_LINK_SPLASHKIT)
            cmd += ["-o", self.meta["name"]]
        else:
            print(f"{self.meta['name']: Unknown language {self.meta['language']}")

        print(f"Building {self.meta['name']}...")
        print("-" + " ".join(cmd))
        subprocess.run(cmd)

    def generate_run_scipt(self):
        build_path = os.path.join(os.curdir, self.meta["name"])

        if self.meta["language"] == "cs":
            return f"""
            #!/bin/sh
            cd {build_path} && dotnet run
            """
        elif self.meta["language"] == "cs":
            return f"""
            #!/bin/sh
            cd {build_path} && {self.meta['name']}
            """
        else:
            print(f"{self.meta['name']: Unknown language {self.meta['language']}")

    def es_config(self):
        pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="splashkit arcade package manager")

    parser.add_argument("--cs-arch", help="dotnet compilation architecture to use", default="native")
    parser.add_argument("--cpp-prefix", help="cpp compiler prefix", default="")
    parser.add_argument("--cpp", help="cpp compiler", default="cpp")
    parser.add_argument("PATH", help="path to the package repository", default=os.curdir)
    # parser.add_argument("GAMES", 

    args = parser.parse_args()

