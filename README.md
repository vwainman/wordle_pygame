# Wordle Pygame

A "just for fun" project cloning features of the Wordle game and putting my own spin on it with the help of the pygame library. I do not reserve any rights to the Wordle IP.

Included features:
- Language in english or french
- Single player or local two players (with a blacked out column in each grid)
- Number of guess rows can range from 1 to 8 
- Number of letters can range from 4 to 7

## Requirements

- Python 3.x
- The pygame library

## Usage

```py
from wordle import WordleUI

WordleUI(**dict(arg.split('=') for arg in sys.argv[1:]))
```

Command line keyword arguments:
- mode = "single player" or "multiplayer"
- letters = 4 to 7
- rows = 1 to 8
- language = "english" or "français"
- text_directory_path = "folder path"
- allowed_guesses_file_name = "file name"
- possible_solutions_file_name = "file name"

```bash
$ python wordle.py mode="single player" ...
# or 
$ python wordle.py
# for default play
```

## Development

TODO: fix english wordle files to include variable length words (only works with 5 letters as of now)
TODO: add docstrings and unit testing 