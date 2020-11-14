![badge](https://action-badges.now.sh/artur-shaik/wallabag-client) [![codecov](https://codecov.io/gh/artur-shaik/wallabag-client/branch/master/graph/badge.svg?token=INPHCV9VDO)](https://codecov.io/gh/artur-shaik/wallabag-client) [![PyPI version shields.io](https://img.shields.io/pypi/v/wallabag-client.svg)](https://pypi.python.org/pypi/wallabag-client/)

# wallabag-client

Wallabag-client is a command line client for the self hosted read-it-later app [wallabag](https://www.wallabag.org/). Unlike to other services, wallabag is free and open source.

Wallabag-client is refactored version of existed wallabag-cli tool.

--------------------------------------------------------------------------------

## Features

- List entries (filterable);
- Show the content of an entry;
- Add new entries;
- Delete entries;
- Mark existing entries as read;
- Mark existing entries as starred;
- Change the title of existing entries;
- Tags support;
- Annotations support;
- Opening entries in browser;
- Showing entry information.

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
  anno            Annotations command
  config
  delete          Delete an entry from wallabag.
  delete-by-tags  Delete entries from wallabag by tags.
  info            Information command
  list            List the entries on the wallabag account.
  open            Open entry in browser
  read            Toggle the read-status of an existing entry.
  show            Show the text of an entry.
  star            Toggle the starred-status of an existing entry.
  tags            Retrieve and print all tags.
  update          Toggle the read or starred status or change the title of...
  update-by-tags  Set the read or starred status of an existing entries...
```
