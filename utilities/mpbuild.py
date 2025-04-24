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
    [... existing docstring ...]
    """
    # Disconnect and check port
    disc()
    serial_port = check_port(port, verbose)
    if serial_port is None:
        click.echo("No valid ports found, re-run with -p option")
        sys.exit(1)

    # Initialize board connection
    click.echo(f"Building uP app using {build} file on {serial_port} port")
    uPbd = initialize_board_connection(serial_port)

    # Check if board is empty
    check_board_empty(uPbd, verbose)

    # Process build file
    dirs = process_build_file(build, uPbd, dryrun, verbose)

    # Display results
    display_results(uPbd, dirs)

    # Clean up
    cleanup_connection(uPbd)


def initialize_board_connection(serial_port):
    """Initialize connection to the board"""
    uPbd = SerialTransport(serial_port, 115200)
    uPbd.enter_raw_repl()
    return uPbd


def check_board_empty(uPbd, verbose):
    """Check if the board's flash memory is empty"""
    local_files = uPbd.fs_listdir("/")
    if len(local_files) != 0:
        click.echo("Flash memory not empty, delete files and try again.")
        if verbose:
            click.echo("Files on board are the following: ")
            for file in local_files:
                if file[3] == 0:
                    click.echo(f"{file[0]}/")
                else:
                    click.echo(f"{file[0]: >20}\t{file[3]}")
        sys.exit()


def process_build_file(build_file, uPbd, dryrun, verbose):
    """Process the build file and deploy files to the board"""
    dirs = []
    with open(build_file, 'r') as files:
        file_list = files.readlines()

    with click.progressbar(file_list) as progressbar:
        for file in progressbar:
            process_file(file, uPbd, dirs, dryrun, verbose)

    return dirs


def process_file(file, uPbd, dirs, dryrun, verbose):
    """Process a single file line from the build file"""
    if verbose:
        click.echo(f"{file.strip()}")

    if folder.match(file):
        d = file.strip()
        dirs.append(d)
        if dryrun:
            click.echo(f"uPbd.fs_mkdir({d})")
        else:
            uPbd.fs_mkdir(d)

    elif comment.match(file):
        return

    elif main_prog.match(file):
        s = file[1:].strip()
        if dryrun:
            click.echo(f"uPbd.fs_put({s}, main.py)")
        else:
            uPbd.fs_put(s, 'main.py')

    elif change.match(file):
        s, d = file[1:].split(',')
        if dryrun:
            click.echo(f"uPbd.fs_put({s}, {d.strip()})")
        else:
            uPbd.fs_put(s, d.strip())

    else:
        s = file.strip()
        if dryrun:
            click.echo(f"uPbd.fs_put({s}, {s})")
        else:
            uPbd.fs_put(s, s)


def display_results(uPbd, dirs):
    """Display the results of the build process"""
    click.echo("/")
    uPbd.fs_ls('/')  # type: ignore
    for d in dirs:
        click.echo(f"{d}/")
        uPbd.fs_ls(d)   # type: ignore


def cleanup_connection(uPbd):
    """Clean up the board connection"""
    uPbd.exit_raw_repl()
    uPbd.close()
    conn()
