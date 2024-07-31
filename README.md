# Flipper

The splashkit arcade machine games repository.

## Adding a game

Create a new directory with the name of your game. Inside this directory we're
going to want to create the following files

- meta
- build
- run

### The meta file

The meta file contains data about your game. A minimal example of which is below.

```bash
NAME=""
SOURCE=""
```

An example of a fleshed out meta file might look like

```bash
NAME="Foobar"
DESCRIPTION="Foobar is an amazing strategy game based on fizzbuzz"
SOURCE="https://github.com/thoth-tech/foobar.git"
IMAGE="foobar.png"
```

where

- `NAME` is the game of your game
- `DESCRIPTION` is a short description of your game (optional)
- `SOURCE` is a github repository containing the code of your game
- `IMAGE` is a path to a an image inside your source repository which will be
  used as the splash screen for your game (optional)

### The build file

The build file contains the commands you use to compile your game. Just be
weary that you're build script needs to cross compile your game for the armhf
(also known as arm32) architecture so that it can run on the Raspberry Pi. See
below for examples of various languages

**DotNet**

```bash
dotnet build --arch linux-arm
```

**C++**

```bash
arm-linux-gnueabihf-g++ game.cpp -l Splashkit -o game
```

**Python**

Python doesn't require any compiling so the build file can be left blank.

### The run file

The run file contains the commands used to run your game. Below are some
examples for different languages.

**DotNet**

TODO: is dotnet installed on the arcade machine? If not we'll need to use
something like `bin/Debug/net6.0/game`

```bash
dotnet run
```

**C++**

Execute the binary built earlier, the name of which is specified by the `-o`
argument in the build command

```
./game
```

**Python**

Run your python script.

```
python game.py
```

## Advanced usage notes

All the files in your game directory (meta, build and run) are simply just bash
scripts meaning that there is a lot of flexibility to customise how your game
is built and ran.

For an example, if you had third party libraries as submodules, you could run
git submodule in your build script inorder to pull them down.

```bash
git submodule update --init --remote
arm-linux-gnueabihf-g++ game.cpp -l Splashkit -o game
```

Or if your game uses a build system such as cmake or make files you could call
those in your build script. Just remember that your build has to target the
armhf architecture meaning that, for cmake, you'll need to create a [toolchain
file](https://cmake.org/cmake/help/book/mastering-cmake/chapter/Cross%20Compiling%20With%20CMake.html).

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=arcade-machine.cmake .
make
```

The same applies to the run file. If your game requires runtime arguments then
they can be added like so

```bash
./game --high-score-file ./highscores.txt
```

Or maybe your game requires certain files or folders to be present when the
game is ran

```bash
mkdir -p ./saves
./game
```

## Licensing

By using this project to package your game, you are agreeing that a copy of the
source code and a binary build of the game will be freely redistributed.

Please consider licensing your game using an open source license such as GPL,
MIT, Apache or BSD and including a copy of said licence in your game
repository. This way we can freely use your game and avoid copyright law
issues.

This project and all the game packaging files within (not the contents of the
games themselves) are licensed under the MIT license unless otherwise stated.
See LICENSE.txt for more information.
