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
import logging
import sys

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

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-orthanc_push orthanc_push                 \
                /incoming /outgoing

    DESCRIPTION

        `orthanc_push` is an app to push/upload dicoms to an orthanc server

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
    MIN_CPU_LIMIT           = 2000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 8000  # Override with memory MegaByte (MB) limit as int
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
                            


    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        
        # Output the space of CLI
        d_options = vars(options)
        for k,v in d_options.items():
            print("%20s: %-40s" % (k, v))
        print("")
        
        # Create a logger object
        logger = logging.getLogger()
            
        # set level 
        logger.setLevel(logging.INFO)
        
        # add handler
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        
        # lets create a log file in the o/p directory first
        log_file = os.path.join(options.outputdir,'progress.log')

        lf = open(log_file,"w")
        
        # now create and configure logger
        file_handler = logging.FileHandler(log_file)
        
        # add handler
        logger.addHandler(file_handler)
        
        orthanc = Orthanc(options.orthancUrl,username=options.username,password=options.password)
        dcm_str_glob = '%s/%s' % (options.inputdir,options.inputFileFilter)
        l_dcm_datapath = glob.glob(dcm_str_glob, recursive=True)
        
        modality = RemoteModality(orthanc,options.pushToRemote) 
        
        data={}
        for dcm_datapath in l_dcm_datapath:
            logger.info(f"Pushing dicom: {dcm_datapath} to orthanc \n")
            with open(dcm_datapath, 'rb') as file:
            
                try:
                    data = orthanc.post_instances(file.read())                
                except Exception as err:
                    logger.info(f'{err} \n')
                    
                if len(options.pushToRemote)>0:
                    resource_id = data['ID'] 
                    logger.info(f'Pushing resource {resource_id} to {options.pushToRemote} \n')
                    
                    try:                   
                        response = modality.store( {'Resources':[resource_id]})
                        logger.info(f'Response : {response}\n')
                    except Exception as err:
                        logger.info(f'{err} \n')
                
        # Close logging
        logger.removeHandler(file_handler)
        file_handler.close()
        lf.close()
        
       

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
