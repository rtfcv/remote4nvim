import psutil
import json
import subprocess

import os
import os.path
import tempfile

import argparse


def r4n(args):
    ''' Main Function for remote4nvim
    '''
    TEMP = tempfile.gettempdir() # this mechanism should be improved...
    pidFile = os.path.join(TEMP, 'nvimRemotePid.json')

    # obj containing neovim process info
    nvimProc = {}

    # try to read the PID file
    if os.path.isfile(pidFile):
        with open(pidFile) as jsonFile:
            nvimProc = json.load(jsonFile)

    myPid = None
    myServ = ''
    try:
        # assert type(nvimProc) == dict # this should be dict
        myPid = nvimProc['pid']
        myServ = nvimProc['server']
    except BaseException as e:
        # the keys that should have existed did not for some reason
        print(e.__class__.__name__, ': ', e)
        # reset the process info dict
        nvimProc = {}

    myProc = None
    if (myPid is not None) and psutil.pid_exists(myPid):
        # server address was retrieved and PID was alive
        myProc = psutil.Process(myPid)
        print('running: ', myProc.cmdline())
        newProc = psutil.Popen(['nvim', '--server', myServ, '--remote', *(args.files)])
    else:
        # either myPid is None or process is dead

        # reset server address
        myServ = '127.0.0.1:7777' # I don't think this should be hardcoded

        # Launch new neovim with specified server #
        myProc = psutil.Popen(
                ['nvim', '--listen', myServ, *(args.files)],
                # shell=True, # let's see if we really need this (we don't for win10)
                # stdout=subprocess.PIPE, # this must be commented out
                # stdin=subprocess.PIPE,  # this must be commented out
                )
        nvimProc['pid'] = myProc.pid
        nvimProc['server'] = myServ

        # write PID file
        with open(pidFile, 'w') as jsonFile:
            nvimProc = json.dump(nvimProc, jsonFile)

        # go back to neovim
        myProc.wait()
    return


def main():
    ''' parse argument and call r4n(args)
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--server',
        help='server func'
    )

    parser.add_argument(
        'files', nargs='*', type=str,
        help='Project IDs from [modrinth](https://modrinth.com/)'
    )

    args = parser.parse_args()

    if args.server is not None:
        print(args)
        if hasattr(args, 'files'):
            print()
    else:
        r4n(args)


if __name__ == '__main__':
    main()
