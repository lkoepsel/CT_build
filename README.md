# CT_build: CoolTerm & Sublime Text package for scripting capabilities

### Repository was previously CoolTerm_pip 
### CoolTerm_pip has been deprecated, please use this repository

A python package providing scripting capability for [CoolTerm](https://freeware.the-meiers.org) along with [Sublime Text](https://www.sublimetext.com/index2) for automating activities for MicroPython, C and FlashForth. By installing via `pip`, one can easily use the scripting capabilities of CoolTerm via *python*.

## Description
Its useful to move the focus to *CoolTerm*, once a automated *build* or *upload* has been completed. This scripting enhancement allows you to immediately begin interacting with the microcontroller using *CoolTerm*. The connection script will make the appropriate changes required for activating the *CoolTerm* window on *macOS* (using *AppleScript*) or on *Windows* (using *pygetwindow*). 

In this example, I use the *build system* on *Sublime Text 4* (**ST4**).

## Platforms
I've been able to get this to work well on *macOS* and *Windows*. I have been unsuccessful on *Linux*.
 
## Installation

### 1. Clone the repository and install
```bash
git clone git@github.com:lkoepsel/CT_build.git
# change to the directory
cd CT_build
# install software
pip install .
```
### OR Install from GitHub

```bash
pip install git+https://github.com/lkoepsel/CT_build
```

### 2. Activate CoolTerm scripting
To use scripting with CoolTerm, you will need to enable it in Preferences. Go to CoolTerm -> Preferences -> Scripting and check the box `Enable Remote Control Socket`. If on the Mac, be sure to check `Enable AppleScript`. If you see the error *"Could not connect to CoolTerm"*, more than likely it is due to not enabling this preference. 

## Add build automation to Sublime Text 4 (ST4)
### AVR_C - automates `make` commands for building C programs on the Uno (*AVR family*)
Save this file as *Make AVR_C.sublime-build* using Tools -> Build System -> New Build System in **ST4**
```json
{
	"cmd": "make",
	"shell_cmd": "ct_disc && make flash && ct_conn",
	"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
	"selector": "source.makefile",
	"keyfiles": ["Makefile", "makefile"],

	"variants":
	[
		{
			"name": "Flash only",
			"shell_cmd": "ct_disc && make flash && ct_conn"
		},
		{
			"name": "All new",
			"shell_cmd": "make LIB_clean && make clean && make"
		},
		{
			"name": "Clean",
			"shell_cmd": "make clean"
		},
	]
}
```
### FlashForth - automates uploading a file to a board running FlashForth
Save as *FlashForth.sublime-build* using Tools -> Build System -> New Build System in ST4. There are two versions to upload to the *Uno*:
1) No delays - if upload finishes successfully, continue to use
2) Slight delay per line - if upload seems to overwhelm FlashForth, you can slow it down using the -n option. 
```json
{

	"variants":
	[
		{
			"name": "Send to board (normal speed) and activate CoolTerm",
			"shell_cmd": "up $file"
		},
		{
			"name": "Send to board (slower speed) and activate CoolTerm",
			"shell_cmd": "up -n 3 $file"
		}
	]

}
```
#### MicroPython - automates uploading a script to a processor running MicroPython
Save this file as *MicroPython.sublime-build* using Tools -> Build System -> New Build System in **ST4**
```json
{

	"variants":
	[
		{
			"name": "Copy to main.py and activate CoolTerm",
			"shell_cmd": "ct_disc && mpremote cp $file :main.py && mpremote reset && ct_conn"
		},
		{
			"name": "Copy to same filename and activate CoolTerm",
			"shell_cmd": "ct_disc && mpremote cp $file :$file_name && mpremote reset && ct_conn"
		},
		{
			"name": "Cross compile same filename for upload",
			"shell_cmd": "mpy-cross-v6.1 -march=armv6m $file"
		}
	]

}
```
## Building a MicroPython Application - `mpbuild`
This repo also installs `mpbuild` which allows you to build an application by creating a text file containing the instructions as to how/where to copy files required for the application. 

Detailed explanation can be found in my repository [microserver](https://github.com/lkoepsel/microserver). In short:

1. Remove all files from board: `mpremote littefs_rp2`
2. Build application: `mpbuild application.txt`

 
## Other Usage Examples
1. **Make sure you turn on "Enable Remote Control Socket" under "Scripting" in the Preferences**. 
2. Follow the example scripts contained in the CoolTerm documentation, *CoolTerm -> Scripting -> Python -> Examples*

## Connect and Disconnect Scripting
My main scripting requirement is to have my editor, *ST4*, disconnect CoolTerm, upload code then reconnect *CoolTerm*. When installed via `pip`, there will be two CLI commands which will disconnect and connect/activate CoolTerm. You can run the commands below in the command line or use them in a script of your design. 

### Disconnect - `ct_disc`
To disconnect CoolTerm from the serial port, use `ct_disc` in your scripts.

### Connect - `ct_conn`
To disconnect CoolTerm from the serial port, use `ct_conn` in your scripts.

## Notes
1. This repository contains the CoolTerm python program, *CoolTerm.py*, which is contained in the CoolTerm application download. It will be updated when CoolTerm is updated.

## Documentation for Installed Commands
### up - for building FlashForth applications
```bash
up --help
Usage: up [OPTIONS] FORTHFILE

  Builds an FlashForth application on a board. Use with Sublime Text build
  automation https://github.com/lkoepsel/CT_build

  * Requires a text file containing FlashForth words
  * -p port is not required, use if up is not finding the proper serial port,
  it will guess using 'usbmodem' or 'COM' as an indicator
  * Use '-c' to view the exact lines which are transferred, before transfer,
  file is cleaned of all comments, increasing transfer speed
  * Use '-v' to view the response line for each line transmitted,
  this allows for more detailed debugging
  * Use '-d n' for a n*10ms delay between lines, use if upload has
  errors uploading due to transfer speed
  * Use '-b n' for the serial baud rate, FlashForth has been tested with
  250000 and it works well, stock FlashForth is 38400

Options:
  --version                 Show the version and exit.
  -p, --port TEXT           Port address (e.g., /dev/cu.usbmodem3101, COM3).
  -c, --clean               Print clean file to be transferred and exit.
  -d, --delay_line INTEGER  delay in milliseconds * 10 per line, default is 0
  -b, --baud INTEGER        baud rate of serial port, default is 1,000,000
  -v, --verbose             print response to every line
  --help                    Show this message and exit.
  ```

  ### mpbuild - for building MicroPython applications
  ```bash
  mpbuild --help
Usage: mpbuild [OPTIONS] BUILD

  Builds an MicroPython application on a board. Uses a text file containing
  names of folders and files to copy files and create folders, approriately to
  a board running MicroPython. Requires -p port for serial port: as in -p
  /dev/cu.usb... or -p COM3 Board storage must be empty or program exits.

  Detailed example: https://github.com/lkoepsel/microserver

  * Requires a text file containing the following:
  * Filenames can NOT have blanks in their names.
  * lines starting with '\n *' are comments and ignored
  * lines starting with '/' are directories and are created
  * lines starting with '!' are files to be copied and renamed,
  + 2 fields are required, separated by a ', ', localname, piconame
  * 1 line starting with '+' will be copied to main.py
  * directory lines must be prior to the files in the directories
  * all other lines are valid files in the current directory
  * -p port required to set to board serial port

Options:
  --version        Show the version and exit.
  -p, --port TEXT  Port address (e.g., /dev/cu.usbmodem3101, COM3).
  -n, --dry-run    Show commands w/o execution & print file format.
  --verbose        Print actions being performed.
  --help           Show this message and exit.
  ```

