#!/usr/bin/env python

base_url = "https://panel.orionvm.com.au/api/"

import sys
import json
import base64
import urllib
import urllib2
import logging
import time
import argparse
import subprocess
from getpass import getpass

logging.basicConfig()
logger = logging.getLogger("ovmfg")
logger.setLevel(logging.DEBUG)



def parse_args(argv):
    p = argparse.ArgumentParser(description="Run an OrianVM vm in the console foreground")
    p.add_argument("hostname", metavar="ORIONVM_HOSTNAME",
            type=str, nargs=1,
            help="The OrionVM hostname of the vm you whish to run")
    p.add_argument("-u", "--user", metavar="USERNAME",
            type=str, nargs=1,
            help="Your OtionVM username")
    p.add_argument("-p", "--password", metavar="PASSWORD",
            type=str, nargs=1,
            help="Your OrionVM password. By ommiting this you will be prompted for the password")
    p.add_argument("-t", "--time", metavar="SECONDS",
            type=int, nargs=1,
            help="If specified, after SECONDS elaps finsih and shutdown the vm")
    p.add_argument("-w", "--wait", metavar="SECONDS",
            type=int, nargs=1, default=60,
            help="Time to wait before running COMMAND (default: 60 seconds)")
    p.add_argument("command", metavar="COMMAND",
            type=str, nargs="?",
            help="If present, run COMMAND taking the rest of the command line as options for COMMAND. When" +
            " COMMAND finishes shutdown the vm")
    p.add_argument("command_options", metavar="OPTION",
            type=str, nargs="*",
            help="Options to be passed to  COMMAND") 

    return p.parse_args(argv)

def json_request(url, headers, data=None):

    if data:
        data = urllib.urlencode(data.items())


    req = urllib2.Request(
            url = base_url + url,
            headers=headers,
            data=data)

    stream = urllib2.urlopen(req)
    obj = json.load(stream)

    stream.close()
    return obj

def main(argv=sys.argv):

    cmd_args = parse_args(argv[1:])

    hostname  = cmd_args.hostname[0]
    user      = (cmd_args.user or [raw_input("OrionVM username: ")])[0]
    password  = (cmd_args.password or [getpass("OtionVM password: ")])[0]
    wait_time = (cmd_args.time or [None]) [0]
    command   = cmd_args.command or None
    command_wait    = cmd_args.wait
    command_options = cmd_args.command_options

    # Get authentication header

    auth = "Basic " + base64.b64encode("%s:%s" % (user, password))
    headers = {"Authorization": auth}

    logger.info ("Searching vm_pool for %s", hostname)
    try:
        vm_pool = json_request ("vm_pool", headers)
    except Exception, e:
        logger.error ("Was not able to get vm_pool")
        raise e

    # Select vm by hostname

    selected_vm = [v for v in vm_pool if v["hostname"] == hostname]
    if len(selected_vm) ==0:
        raise Exception ("Could not find vm '%s'" % hostname)
    vmid = int(selected_vm[0]["vm_id"])
    logger.info ("Found vm with vmid: %s", vmid)


    # Start the VM

    logger.info ("Starting %s", hostname)
    try:
        deploy_result = json_request ("deploy", headers, {"vmid": vmid})
    except urllib2.URLError, e:
        logger.error ("Was not able to request a deploy")
        raise e

    if not deploy_result:
        raise Exception ("Could not start vm")


    logger.info ("VM Started")

    if command is not None:

        # run a command

        logger.info("Waiting for %s seconds til starting %s", command_wait, command)
        time.sleep(command_wait)
        logger.info("Running %s", " ".join([command] + command_options))
        subprocess.call([command] + command_options)
        logger.info("%s terminated.", command)

    else:

        # do a wait

        try:
            if wait_time is not None:
                logger.info("Waiting %s seconds or until interupted (type: Ctrl-C)", wait_time)
                time.sleep(wait_time)
            else:
                logger.info("Waiting indefinatly until interupted (type: Ctrl-C)")
                while(True):
                    time.sleep(1)
        except KeyboardInterrupt:
            pass
        logger.info("KeyboardInterrupt detected")


    # give oportunity for user to cancel a shutdown

    logger.info ("Will shutdown the vm in 5 seconds - you can abort this and leave it up by interupting now")
    time.sleep(5)


    # shutdown

    try:
        shutdown_result = json_request ("action", headers, {"vmid":vmid,"action":"shutdown"})
    except urllib2.URLError, e:
        logger.error ("Was not able to request a shutdown")
        raise e

    logger.info("action shutdown result: %s", shutdown_result)

    return 0;


if __name__ == "__main__":
    sys.exit(main(sys.argv))

