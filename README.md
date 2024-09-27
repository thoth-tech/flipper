# Flipper

The splashkit arcade machine games repository.

## Adding a game

Adding a game is as easy as creating a new [toml](https://toml.io) file which
contains some details about your game. An example of a basic game is below.

```toml
[meta]
name = "FooBar"
description = "Foobar is an amazing strategy game based on fizzbuzz"
language = "cpp"

[git]
repo = "https://github.com/thoth-tech/foobar.git"
```

The toml file is broken down into 2 parts meta and git.

### meta

The meta section contains metadata about the game. It's fields are as follows.

- `name` is the name of the game
- `description` is a short description of the game
- `language` the language which the game is programmed in. Possible values are
  `cpp` for C++ or `cs` for C#. Python and pascal support coming soon.

### git

The git section contains information about the github repository containing the
game's source code.

- `repo` is the url of the game's github repository

## Full reference

The above example is only the minimum required to package a game. Below shows
all the possible configuration values, however everything which is not stated
above is considered optional.

```toml
[meta]
name = ""
description = ""
language = ""

[git]
repo = ""
branch = ""  # a tag can also be specified
directory = ""

# See https://github.com/thoth-tech/ArcadeMenu/blob/master/GAMELISTS.md
[emulationstation]
image = ""
thumbnail = ""
rating = 0.0
releasedate = 1979-05-27T07:32:00
developer = ""
publisher = ""
genre = ""
players = 0
```

## FAQ

> Why toml?

A toml parser included in Python's standard library, where as a yaml parser
isn't, and one of my requirements was that the build script should have no
dependencies other then python and it's standard library.

## Usage

Flipper is designed to be ran in a clean 'build' directory (similar to cmake)
and therefore takes the path to the repository as a positional argument. This
would also allow one to seperate the games repository from the flipper source
if flipper is being used on more repositories then just this one.

A typical usage would look like the following

```
$ mkdir build
$ cd build
$ ../flipper.py ..
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
