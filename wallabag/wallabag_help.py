"""
This is the internal help system of wallabag-cli.
"""


def show(startscript, command="main"):
    """
    Main function for showing help texts.
    """
    if command == "":
        command = "main"

    index = dict()

    # General help
    main_txt = """
Usage:
  {0} <command> [options]

Commands:
  config         Start the configuration.
  add            Add a new entry to wallabag.
  delete         Delete an entry.
  list           List the entries on the wallabag account.
  update         Change the read- or starred-status of an existing entry or change the title.

General Options:
  -h, --help     Show help.
  --about        Show about information.
  -v, --version  Show version No.

Use \"{0} <command> --help\" for further information.
And don't forget to be excellent to each other!
""".format(startscript)
    index['main'] = main_txt

    # config
    config_txt = """
Usage:
  {0} config [options]

Description:
  Start the configuration.

Options:
  -h, --help      Show help
  -c, --check     Check the config for errors
  -p, --password  Change the wallabag password
  -o, --oauth     Change the wallabag client credentials
""".format(startscript)
    index['config'] = config_txt

    # add
    add_txt = """
Usage:
  {0} add [options] <url>

Description:
  Add a new link to wallabag.

Options:
  -h, --help           Show help
  -t, --title <title>  Add a custom title
  -s, --starred        Mark as starred
  -r, --read           Mark as read
""".format(startscript)
    index['add'] = add_txt

    # delete
    delete_txt = """
Usage:
  {0} delete [options] <entry-id>

Description:
  Delete an entry from wallabag. The entry-id can be found in "{0} list" for example.

Options:
  -h, --help   Show help
  -f, --force  Do not ask before deletion
""".format(startscript)
    index['delete'] = delete_txt

    # list
    list_txt = """
Usage:
  {0} list [options]

Description:
  Gives a summary of entries in wallabag. Use options to filter the results.

Options:
  -h, --help                  Show help
  -c, --count <"all"|number>  Set the number of entries to show
  --unread                    Show only unread entries (default)
  -r, --read                  Show only read entries
  -a, --all                   Show read as well as unread entries
  -s, --starred               Show only starred entries
  -u, --unstarred             Show only unstarred entries
  -o, --oldest                Show oldest matches instead of the newest
  -f, --full                  Do not trim the titles to fit the length of the cli
""".format(startscript)
    index['list'] = list_txt

    # update
    update_txt = """
Usage:
  {0} update [options] <entry-id>

Description:
  Toggle the read- or starred status or change the title of an existing entry. The entry-id can be found in "{0} list" for example.

Options:
  -h, --help             Show help
  -r, --read             Toggle the read-status
  -s, --starred          Toggle the starred-status
  -t, --title <"title">  Change the title
""".format(startscript)
    index['update'] = update_txt

    if not command in index:
        print("Error: Invalid command \"{0}\"!".format(command))
        command = "main"

    print(index[command])
