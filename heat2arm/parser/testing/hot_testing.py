# Copyright 2015 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
    This module contains constants to be used for testing the behavior
    of the parser against various Heat template scenarios.
"""

# DUMMY_TEST_TEMPLATE contains the bare minimum of fields required of a
# template. It is useful in tests which do not depend on the data
# of the input template itself.
DUMMY_TEST_TEMPLATE = """
parameters: {}
resources: {}
"""[1:]

# PROCESSED_TEST_TEMPLATE contains the data of a template which contains no
# actual templating function usage. It useful for testing aspects which
# imply using an already processed template.
PROCESSED_TEST_TEMPLATE = """
parameters:
    simple_param:
        default: simple_string
    advanced_param:
        default: ["An", "unexpected", "list"]
    no_default:
        description: "has no 'default' value"
    resource_param:
        default: prioritised

resources:
    dummy_resource:
        type: SOME::RANDOM::TYPE
        properties:
            prop: val
            list_prop: ["this", "is", "a", "list"]
            dict_prop:
                key1: value 1
                key2: value 2
            nested_prop:
                nested_string: a string
                nested_list: ["val1", { key: value }, "val2"]
                nested_dict:
                    key: value
                    list: [1, 2, 3]
    resource_param: {}
"""[1:]


# COMPLETE_TEST_TEMPLATE contains the raw data of a template to be used
# advanced parsing behavioral tests.
COMPLETE_TEST_TEMPLATE = """
heat_template_version: 2013-05-23

description: >
  HOT template to create a new neutron network plus a router to the public
  network, and for deploying two servers into the new network. The template also
  assigns floating IP addresses to each server so they are routable from the
  public network.

parameters:
  key_name:
    type: string
    description: Name of keypair to assign to servers
  image:
    type: string
    description: Name of image to use for servers
    default: ubuntu.12.04.LTS.x86_64
  flavor:
    type: string
    description: Flavor to use for servers
    default: m1.small
  public_net:
    type: string
    description: >
      ID or name of public network for which floating IP addresses will be allocated
  private_net_name:
    type: string
    description: Name of private network to be created
    default: "asdasd"
  private_net_cidr:
    type: string
    description: Private network address (CIDR notation)
    default: "10.0.0.0/24"
  private_net_gateway:
    type: string
    description: Private network gateway address
    default: "10.0.0.1"
  private_net_pool_start:
    type: string
    description: Start of private network IP address allocation pool
    default: 10.0.0.100
  private_net_pool_end:
    type: string
    description: End of private network IP address allocation pool
    default: 10.0.0.200

resources:
  private_net:
    type: OS::Neutron::Net
    properties:
      name: { get_param: private_net_name }

  private_subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: private_net }
      cidr: { get_param: private_net_cidr }
      gateway_ip: { get_param: private_net_gateway }
      allocation_pools:
        - start: { get_param: private_net_pool_start }
          end: { get_param: private_net_pool_end }

  router:
    type: OS::Neutron::Router
    properties:
      external_gateway_info:
        network: { get_param: public_net }

  router_interface:
    type: OS::Neutron::RouterInterface
    properties:
      router_id: { get_resource: router }
      subnet_id: { get_resource: private_subnet }

  server1:
    type: OS::Nova::Server
    properties:
      name: Server1
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - port: { get_resource: server1_port }

  server1_port:
    type: OS::Neutron::Port
    properties:
      network_id: { get_resource: private_net }
      fixed_ips:
        - subnet_id: { get_resource: private_subnet }

  server1_floating_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: { get_param: public_net }
      port_id: { get_resource: server1_port }

  server2:
    type: OS::Nova::Server
    properties:
      name: Server2
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - port: { get_resource: server2_port }

  server2_port:
    type: OS::Neutron::Port
    properties:
      network_id: { get_resource: private_net }
      fixed_ips:
        - subnet_id: { get_resource: private_subnet }

  server2_floating_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: { get_param: public_net }
      port_id: { get_resource: server2_port }

outputs:
  server1_private_ip:
    description: IP address of server1 in private network
    value: { get_attr: [ server1, first_address ] }
  server1_public_ip:
    description: Floating IP address of server1 in public network
    value: { get_attr: [ server1_floating_ip, floating_ip_address ] }
  server2_private_ip:
    description: IP address of server2 in private network
    value: { get_attr: [ server2, first_address ] }
  server2_public_ip:
    description: Floating IP address of server2 in public network
    value: { get_attr: [ server2_floating_ip, floating_ip_address ] }
"""[1:]
