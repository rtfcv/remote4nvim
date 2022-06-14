import psutil
import json

import os
import os.path
import tempfile

import argparse
import logging
import sys

LOG = logging.getLogger('remote4nvimLogger')


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
        LOG.warn(f'{e.__class__.__name__} : {e}')
        # reset the process info dict
        nvimProc = {}

    myProc = None
    if (myPid is not None) and psutil.pid_exists(myPid):
        # server address was retrieved and PID was alive
        myProc = psutil.Process(myPid)
        LOG.info(f'running: {myProc.cmdline()}')
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
        help='NOT IMPLEMENTED: server func'
    )
    parser.add_argument(
        '--debug',
        help='DO NOT USE. Print debug info.',
        action='store_true'
    )

    parser.add_argument(
        'files', nargs='*', type=str,
        help='Files to edit'
    )

    args = parser.parse_args()

    if args.debug:
        LOG.addHandler(logging.StreamHandler(sys.stdout))
        LOG.setLevel(logging.DEBUG)
        LOG.info('Debug Active')
        LOG.info(str(args))

    if args.server is not None:
        print('NOT IMPLEMENTED!!!')
        print('The args were: ', args)
        if hasattr(args, 'files'):
            print('The file list was: ', args.files)
    else:
        r4n(args)


if __name__ == '__main__':
    main()
