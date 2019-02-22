# -*- python -*-
# ex: set filetype=python:

import os.path
from buildbot.plugins import *


mvn_lock = util.WorkerLock("mvn_lock",
                             maxCount=1)

def getMavenLock():
  return mvn_lock

def getMavenBase():
{% if skip_tests %}
    return ['mvn', '-B', '-V', '-Dmaven.repo.local=/builder/m2', '-DskipTests']
{% else %}
    return ['mvn', '-B', '-V', '-Dmaven.repo.local=/builder/m2']
{% endif %}

def getClone():
    return steps.GitHub(
        repourl="{{ source_repo_url }}",
        mode='incremental',
        method='fresh',
        haltOnFailure=True,
        flunkOnFailure=True,
        name="Clone/Checkout")

def getWorkerPrep():
    command = getMavenBase()
    command.extend(['dependency:go-offline', '-fn'])
    return steps.ShellSequence(
        commands=[
            util.ShellArg(command=['git', 'clean', '-fdx'], logfile='clean'),
            util.ShellArg(
                command=command,
                logfile='deps')
        ],
        haltOnFailure=True,
        flunkOnFailure=True,
        name="Build Prep",
        locks=[mvn_lock.access('counting')])

def getBuild():
    command = getMavenBase()
    command.extend(['clean', 'install'])
    return steps.ShellCommand(
        command=command,
        haltOnFailure=True,
        flunkOnFailure=True,
        name="Build",
        locks=[mvn_lock.access('counting')])

def getPermissionsFix():
    return steps.MasterShellCommand(
        command=["chown", "-R", "{{ buildbot_uid['ansible_facts']['getent_passwd']['buildbot'][1] }}:{{ buildbot_gid['ansible_facts']['getent_group']['buildbot'][1] }}",
            util.Interpolate(os.path.normpath("{{ build_base }}"))
        ],
        name="Fixing directory permissions on buildmaster")

def getClean():
    return steps.ShellSequence(
        commands=[
            util.ShellArg(command=['git', 'clean', '-fdx'], logfile='git'),
        ],
        haltOnFailure=True,
        flunkOnFailure=True,
        name="Cleanup")
