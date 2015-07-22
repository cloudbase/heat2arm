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
  sudo apt-get install -y git python-pip python-dev python-cffi python-lxml libssl-dev python-oslo.config

**CentOS/RHEL 7.0**:
::
  sudo yum install -y epel-release
  sudo yum install -y git gcc python-pip python-devel python-cffi python-lxml openssl-devel python-oslo-config

Heat and heat2arm installation:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Afterwards, we must install a couple of preliminary pypi packages:
::
  sudo pip install pbr routes

Then, considering Heat's components have no pypi packages, we must clone the project and install them manually:
::
  git clone http://github.com/openstack/heat
  sudo pip install ./heat

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

If you system says it cannot find the executable; you could alternatively run
the main entry point of the module manually:
::
  python ./heat2arm/main.py --in samples/servers_in_new_neutron_net.yaml

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
