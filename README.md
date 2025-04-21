![badge](https://action-badges.now.sh/artur-shaik/wallabag-client) [![codecov](https://codecov.io/gh/artur-shaik/wallabag-client/branch/master/graph/badge.svg?token=INPHCV9VDO)](https://codecov.io/gh/artur-shaik/wallabag-client) [![PyPI version shields.io](https://img.shields.io/pypi/v/wallabag-client.svg)](https://pypi.python.org/pypi/wallabag-client/)

# wallabag-client

Wallabag-client is a command line client for the self hosted read-it-later app [wallabag](https://www.wallabag.org/). Unlike to other services, wallabag is free and open source.

Wallabag-client is refactored version of existed wallabag-cli tool.

You can read additional info [here](https://shaik.link/wallabag-client-features.html)

--------------------------------------------------------------------------------

## Features

- List entries (filterable tabulated output with nerd icons);
- Show the content of an entry with custom width and alignment;
- Add new entries;
- Delete entries;
- Mark existing entries as read;
- Mark existing entries as starred;
- Change the title of existing entries;
- Tags support;
- Annotations support;
- Opening entries in browser;
- Showing entry information;
- Export entry to file.

## Installation

`sudo pip3 install wallabag-client`

## Usage

`wallabag --help`

```
Usage: wallabag [OPTIONS] COMMAND [ARGS]...

Options:
  --config TEXT       Use custom configuration file
  --debug             Enable debug logging to stdout
  --debug-level TEXT  Debug level
  --version           Show the version and exit.
  -h, --help          Show this message and exit.

Commands:
  add             Add a new entry to wallabag.
  anno            Annotation commands.
  config          Start configuration.
  delete          Delete an entry from wallabag.
  delete-by-tags  Delete entries from wallabag by tags.
  export          Export entry to file.
  info            Get entry information.
  list            List the entries on the wallabag account.
  open            Open entry in browser.
  read            Toggle the read-status of an existing entry.
  repl            Start an interactive shell.
  show            Show the text of an entry.
  star            Toggle the starred-status of an existing entry.
  tags            Retrieve and print all tags.
  update          Toggle the read or starred status or change the title of...
  update-by-tags  Set the read or starred status of an existing entries...
```

## Install shell completion (zsh)

A completion script for zsh is provided in the directory `completion/zsh/_wallabag`.

Installation can vary based on your zsh settings and environment. Most importantly, the file has to be placed in one of the directories contained in the `$fpath` variable and then autoloaded.

If you want to install the completion script for all users, you can do the following:

```sh
mkdir -p /usr/local/share/zsh/site-functions
cp _wallabag /usr/local/share/zsh/site-functions
```

and restart zsh.

A better option is to have a directory in your home for local completion scripts, but setting this up is beyond the scope of these instructions. You may refer to [this answer on Stackoverflow](https://stackoverflow.com/a/67161186) for more details.
