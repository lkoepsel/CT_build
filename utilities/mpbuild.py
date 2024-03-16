import click
import re
from mpremote.transport_serial import SerialTransport
import serial.tools.list_ports
import sys
from utilities.CT_connect import conn
from utilities.CT_disconnect import disc


folder = re.compile(r'^/')
comment = re.compile(r'^#')
main_prog = re.compile(r'^\+')
change = re.compile(r'^!')


def check_port(port, verbose):
    for p in sorted(serial.tools.list_ports.comports()):
        if port is None:
            if p.manufacturer == 'MicroPython':
                if verbose:
                    click.echo(f"Found {p.device}, valid device")
                return p.device
            else:
                if verbose:
                    click.echo(f"Found {p.device}, not a valid device")
        else:
            if p.device == port and p.manufacturer == 'MicroPython':
                if verbose:
                    click.echo(f"-p {p.device}, is a valid device")
                return port

    if verbose:
        click.echo("No valid serial ports found.")
    return None


@click.command('build')
@click.version_option("2.1", prog_name="mpbuild")
@click.option('-p', '--port', required=False, type=str,
              help='Port address (e.g., /dev/cu.usbmodem3101, COM3).')
@click.argument('build',
                type=click.Path(exists=True, readable=True),
                required=True)
@click.option('-n', '--dry-run', 'dryrun', is_flag=True, default=False,
              help='Show commands w/o execution & print file format.')
@click.option('--verbose', is_flag=True, default=False,
              help='Print actions being performed.')
def build(port, build, dryrun, verbose):
    """
    Builds an MicroPython application on a board.
    Uses a text file containing names of folders and files to copy files
    and create folders, approriately to a board running MicroPython.
    Requires -p port for serial port: as in -p /dev/cu.usb... or -p COM3
    Board storage must be empty or program exits.

    Detailed example: https://github.com/lkoepsel/microserver

    \b
    * Requires a text file containing the following:
    * Filenames can NOT have blanks in their names.
    * lines starting with '\\n *' are comments and ignored
    * lines starting with '/' are directories and are created
    * lines starting with '!' are files to be copied and renamed,
    + 2 fields are required, separated by a ', ', localname, piconame
    * 1 line starting with '+' will be copied to main.py
    * directory lines must be prior to the files in the directories
    * all other lines are valid files in the current directory
    * -p port required to set to board serial port
    """

    disc()
    serial_port = check_port(port, verbose)
    if serial_port is None:
        click.echo("No valid ports found, re-run with -p option")
        sys.exit(1)

    click.echo(f"Building uP app using {build} file on {serial_port} port")
    uPbd = SerialTransport(serial_port, 115200)
    uPbd.enter_raw_repl()
    with open(build, 'r') as files:
        file_list = files.readlines()

    dirs = []
    local_files = uPbd.fs_listdir("/")
    if len(local_files) != 0:
        click.echo("Flash memory not empty, delete files and try again.")
        if verbose:
            click.echo("Files on board are the following: ")
            for file in local_files:
                if file[3] == 0:
                    # directory, don't print size
                    click.echo(f"{file[0]}/")
                else:
                    # file, print both name and size
                    click.echo(f"{file[0]: >20}\t{file[3]}")
        sys.exit()

    with click.progressbar(file_list) as progressbar:
        for file in progressbar:
            if verbose:
                click.echo(f"{file.strip()}")
            # line begins with a slash, create a dir using the following text
            if folder.match(file):
                d = file.strip()
                dirs.append(d)
                if dryrun:
                    click.echo(f"uPbd.fs_mkdir({d})")
                else:
                    uPbd.fs_mkdir(d)

            # line begins with a #, ignore the line its a comment
            elif comment.match(file):
                continue

            # line begins with a +, copy it to main.py
            elif main_prog.match(file):
                s = file[1:].strip()
                if dryrun:
                    click.echo(f"uPbd.fs_put({s}, main.py)")
                else:
                    uPbd.fs_put(
                        s, 'main.py')

            # line begins with a +, copy it to main.py
            elif change.match(file):
                s, d = file[1:].split(',')
                if dryrun:
                    click.echo(f"uPbd.fs_put({s}, {d.strip()})")
                else:
                    uPbd.fs_put(
                        s, d.strip())

            # all other lines are assumed to be valid files to copy to board
            else:
                s = file.strip()
                if dryrun:
                    click.echo(f"uPbd.fs_put({s}, {s})")
                else:
                    uPbd.fs_put(s, s)

    click.echo("/")
    uPbd.fs_ls('/')
    for d in dirs:
        click.echo(f"{d}/")
        uPbd.fs_ls(d)
    uPbd.exit_raw_repl()
    uPbd.close()

    conn()
