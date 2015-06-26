OpenStack Heat to Azure Resource Manager (ARM) template conversion tool
=======================================================================

The purpose of this tool is to automate the conversion between OpenStack and
Azure template formats, translating source resource types into the target
platform equivalent.

Usage sample
^^^^^^^^^^^^

    heat2arm --in samples/servers_in_new_neutron_net.yaml --out azuredeploy.json

The generated ARM template is now ready for deployment on Azure, e.g.:

    azure login -u <your organizational ID email address>

    azure config mode arm

    azure group deployment create "testDeploy" -g "testResourceGroup" --template-file azuredeploy.json
