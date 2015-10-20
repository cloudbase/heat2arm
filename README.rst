OpenStack Heat to Azure Resource Manager (ARM) template conversion tool
=======================================================================
Outline:
^^^^^^^^

The purpose of this tool is to automate the conversion between OpenStack and
Azure template formats, translating source resource types into the target
platform equivalent.

Installation instructions:
^^^^^^^^^^^^^^^^^^^^^^^^^^

The below installation instructions were tested on **up-to-date** installations
of both Ubuntu 14.04 Server and CentOS.

Installing build prerequisites:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A bare minimum Python build environment must be set up before the actual
installation:

**Ubuntu 14.04**:
::
  sudo apt-get install -y git python-pip python-dev python-cffi

**CentOS/RHEL 7.0**:
::
  sudo yum install -y epel-release
  sudo yum install -y git gcc python-pip python-devel python-cffi

Heat2arm installation:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Afterwards, we must install a couple of preliminary pypi packages:
::
  sudo pip install pbr routes

Lastly, we must now clone and install the converter itself:
::
  git clone http://github.com/cloudbase/heat2arm
  sudo pip install ./heat2arm

Usage sample:
^^^^^^^^^^^^^

After installation, the heat2arm executable should have been generated and 
[ideally] already placed in you system path, so you should be able to 
directly start testing it on some of the provided sample templates:
::
  heat2arm --in samples/servers_in_new_neutron_net.yaml

Checking logs:
^^^^^^^^^^^^^^

It is highly advisable to skim the logs after a translation run to review all
warning messages.
Logging options can be set using the `--logfile` and `--loglevel` arguments as follows:
::
  heat2arm --in samples/servers_in_new_neutron_net.yaml --logfile=./heat2arm.log --loglevel=WARNING

By default, the converter will log only warnings to standard error.

Raising issues:
^^^^^^^^^^^^^^^

When reporting an issue with the converter, please include a paste/link to
the logs of the translation run with `--loglevel=debug` set.

Moving forward:
^^^^^^^^^^^^^^^

The ARM template from the above commands may be easily redirected into a file
with the `--out` parameter and can be directly deployed on Azure, either
through the portal_ or using the PowerShell commands:
::
  heat2arm --in input-template.yaml --out azuredeploy.json
  azure login -u <your organizational ID email address>
  azure config mode arm
  azure group deployment create "testDeploy" -g "testResourceGroup" --template-file azuredeploy.json

.. _portal: https://portal.azure.com
