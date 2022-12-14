pl-orthanc_push
================================

.. image:: https://img.shields.io/docker/v/fnndsc/pl-orthanc_push?sort=semver
    :target: https://hub.docker.com/r/fnndsc/pl-orthanc_push

.. image:: https://img.shields.io/github/license/fnndsc/pl-orthanc_push
    :target: https://github.com/FNNDSC/pl-orthanc_push/blob/master/LICENSE

.. image:: https://github.com/FNNDSC/pl-orthanc_push/workflows/ci/badge.svg
    :target: https://github.com/FNNDSC/pl-orthanc_push/actions


.. contents:: Table of Contents


Abstract
--------

An app to push/upload dicoms to an orthanc server and to a remote modality
(if specified)


Description
-----------


``orthanc_push`` is a *ChRIS ds-type* application that takes in DICOMs as input files
and pushes them to a remote Orthanc server and to an optional remote modality


Usage
-----

.. code::

    docker run --rm fnndsc/pl-orthanc_push orthanc_push
        [-f|--inputFileFilter <inputFileFilter>]                    
        [-o|--orthancUrl <orthancServerUrl>]                       
        [-u|--username <orthancUserName>]                          
        [-p|--password <orthancPassword>]                         
        [-r|--pushToRemote <remoteModality>]                     
        [-h|--help]
        [--json] [--man] [--meta]
        [--savejson <DIR>]
        [-v|--verbosity <level>]
        [--version]
        <inputDir> <outputDir>


Arguments
~~~~~~~~~

.. code::

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


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-orthanc_push orthanc_push --man

Run
~~~

You need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-orthanc_push orthanc_push                        \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-orthanc_push .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-orthanc_push nosetests

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
