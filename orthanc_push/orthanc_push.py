#
# orthanc_push ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import os
import glob
from pyorthanc import Orthanc, RemoteModality
from orthanc_api_client import OrthancApiClient
import logging
import sys
import  time
from    loguru              import logger
from    pftag               import pftag
from    pflog               import pflog

from    argparse            import Namespace
from    datetime            import datetime


LOG             = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors = True)
logger.add(sys.stderr, format=logger_format)

Gstr_title = r"""
            _   _                                          _
           | | | |                                        | |
  ___  _ __| |_| |__   __ _ _ __   ___     _ __  _   _ ___| |__
 / _ \| '__| __| '_ \ / _` | '_ \ / __|   | '_ \| | | / __| '_ \
| (_) | |  | |_| | | | (_| | | | | (__    | |_) | |_| \__ \ | | |
 \___/|_|   \__|_| |_|\__,_|_| |_|\___|   | .__/ \__,_|___/_| |_|
                                    ______| |
                                   |______|_|
"""

Gstr_synopsis = """


    NAME

       orthanc_push

    SYNOPSIS

        docker run --rm fnndsc/pl-orthanc_push orthanc_push             \\
            [-f|--inputFileFilter <inputFileFilter>]                    \\
            [-o|--orthancUrl <orthancServerUrl>]                        \\
            [-u|--username <orthancUserName>]                           \\
            [-p|--password <orthancPassword>]                           \\
            [-r|--pushToRemote <remoteModality>]                        \\
            [--pftelDB <DBURLpath>]                                     \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                                 \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing          \\
                fnndsc/pl-orthanc_push orthanc_push                     \\
                /incoming /outgoing

    DESCRIPTION

        `orthanc_push` is an app to push/upload dicoms to an orthanc server.
        It can also instruct that orthanc server to further push data to a
        remote modality.

    ARGS

        [-f|--inputFileFilter <inputFileFilter>]
        A glob pattern string, default is "**/*.dcm", representing the input
        file pattern to analyze.

        [-o|--orthancUrl <orthancServerUrl>]
        URL of the orthanc server.

        [-u|--username <orthancUserName>]
        The username to login to the orthanc server.

        [-p|--password <orthancPassword>]
        Specify the password to login to the orthanc server.

        [-r|--pushToRemote <remoteModality>]
        If specified, orthanc will send dicoms to the target remote modality

        [--pftelDB <DBURLpath>]
        If specified, send telemetry logging to the pftel server and the
        specfied DBpath:

            --pftelDB   <URLpath>/<logObject>/<logCollection>/<logEvent>

        for example

            --pftelDB http://localhost:22223/api/v1/weather/massachusetts/boston

        Indirect parsing of each of the object, collection, event strings is
        available through `pftag` so any embedded pftag SGML is supported. So

            http://localhost:22223/api/vi/%platform/%timestamp_strmsk|**********_/%name

        would be parsed to, for example:

            http://localhost:22223/api/vi/Linux/2023-03-11/posix

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.
"""


class Orthanc_push(ChrisApp):
    """
    An app to push/upload dicoms to an orthanc server
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app to push/upload dicoms to an orthanc server'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 2000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

        self.add_argument(  '--inputFileFilter','-f',
                            dest         = 'inputFileFilter',
                            type         = str,
                            optional     = True,
                            help         = 'Input file filter',
                            default      = '**/*.dcm')

        self.add_argument(  '--orthancUrl','-o',
                            dest         = 'orthancUrl',
                            type         = str,
                            optional     = True,
                            help         = 'Orthanc server url',
                            default      = 'http://0.0.0.0:8042')

        self.add_argument(  '--username','-u',
                            dest         = 'username',
                            type         = str,
                            optional     = True,
                            help         = 'Orthanc server url',
                            default      = 'orthanc')

        self.add_argument(  '--password','-p',
                            dest         = 'password',
                            type         = str,
                            optional     = True,
                            help         = 'Orthanc server url',
                            default      = 'orthanc')

        self.add_argument(  '--pushToRemote','-r',
                            dest         = 'pushToRemote',
                            type         = str,
                            optional     = True,
                            help         = 'Remote modality',
                            default      = '')
        self.add_argument('--timeout', '-t',
                          dest           = 'timeout',
                          type           = int,
                          optional       = True,
                          help           = 'Number of seconds to wait for response while sending to remote PACS',
                          default        = 1000)
        self.add_argument(  '--pftelDB',
                            dest         = 'pftelDB',
                            default      = '',
                            type         = str,
                            optional     = True,
                            help         = 'optional pftel server DB path'
                        )

    def preamble_show(self, options) -> None:
        """
        Just show some preamble "noise" in the output terminal
        """

        LOG(Gstr_title)
        LOG('Version: %s' % self.get_version())

        LOG("plugin arguments...")
        for k,v in options.__dict__.items():
             LOG("%25s:  [%s]" % (k, v))
        LOG("")

        LOG("base environment...")
        for k,v in os.environ.items():
             LOG("%25s:  [%s]" % (k, v))
        LOG("")

    @pflog.tel_logTime(
            event       = 'orthanc_push',
            log         = 'Push DICOMs to orthanc and optionally retransmit'
    )
    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        self.preamble_show(options)

        # lets create a log file in the o/p directory first
        log_file = os.path.join(options.outputdir, 'terminal.log')
        logger.add(log_file)

        # orthanc = Orthanc(options.orthancUrl)# ,username=options.username,password=options.password)
        orthanc = OrthancApiClient(options.orthancUrl,user=options.username,pwd=options.password)



        dcm_str_glob = '%s/%s' % (options.inputdir,options.inputFileFilter)
        l_dcm_datapath = glob.glob(dcm_str_glob, recursive=True)

        instances_ids=[]
        for dcm_datapath in l_dcm_datapath:
            LOG(f"Pushing dicom: {dcm_datapath} to orthanc")
            try:
                instances_ids += orthanc.upload_file(dcm_datapath)
                # instances_ids += instances_id
            except Exception as err:
                LOG(f'{err} \n')

        if len(options.pushToRemote)>0:
            LOG(f'Pushing {len(instances_ids)} resources to {options.pushToRemote} \n')
            try:
                response = orthanc.modalities.send(options.pushToRemote,resources_ids=instances_ids, timeout=options.timeout)
                LOG('Response : {Success}\n')
            except Exception as err:
                LOG(f'{err} \n')

    def show_man_page(self):
        """
        Print the app's man page.
        """
        LOG(Gstr_synopsis)
