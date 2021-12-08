#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author: 
- Peponas Thomas.
module: dev_facts
short_description: Reports Devices information as facts.

description:
- List and reports details about defined AIX Device such as
  Disks, Adapater, Tape ... in Ansible facts.
version_added: '2.9'
requirements:
- AIX >= 7.1 TL3
- Python >= 2.7
options:
  name:
    description:
    - Specifies the name of a Devices component.
    type: str
    default: 'all'
  type:
    description:
    - Specifies the class of Devices component to report information.
  type: str
     default: 'all'
  dev:
    description:
    - Users can provide the existing DEV facts to which the queried facts should be updated.
      If not specified, the DEV facts in the ansible_facts will be replaced.
    type: dict
    default: {}

'''

EXAMPLES = r'''
- name: Gather all Dev facts
  lvm_facts:
- name: Gather VG facts
  lvm_facts:
    name: all
- name: Gather hdisk facts
  lvm_facts:
    name: all
    type: disk
'''

RETURN = r'''
ansible_facts:
  description:
  - Facts to add to ansible_facts about the LVM components on the system.
  returned: always
  type: complex
  contains:
    DEV:
      description:
      - Contains a Dict of Devices.
      returned: success
      type: dict
      elements: dict
      contains:
        name: 
          description: Devices name
          returned: always
          type: str 
        state:
          description: Status of device
          returned: always
          type: str
        attr:
          description: Dict of attributes
          returned: when ask
          type: dict
'''

from ansible.module_utils.basic import AnsibleModule
import re

def load_dev(module, dev_name, dev_class, get_attr, DEV):
    """
    Get the details for the specified Dev or all
    arguments:
        module       (dict): Ansible module argument spec.
        dev_name      (str): Device name.
        dev_class     (str): Device class
        get_attr     (bool): Retrieve Device Attributs
        DEV          (dict): DEV facts.
    return:
        msg  (str): message
        DEV (dict): DEV facts
    """
    msg = ""
    if (dev_class != "all"):
        cmd = "lsdev -Cc %s" % dev_class
    else:
        cmd = "lsdev" 
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        msg += "Command '%s' failed." % cmd
    else:
        for line in stdout.splitlines():
            dev = line.split()[0].strip()
            state = line.split()[1].strip()
            DEV[dev]={}
            DEV[dev]['name']=dev
            DEV[dev]['state']=state
            
            if (get_attr):
                DEV[dev]['attr']={}
                cmd = "lsattr -El %s" % dev
                rc, out, err = module.run_command(cmd)
                if rc != 0:
                    msg += "Command '%s' failed." % cmd
                else:
                    attributes = {}
                    for ln in out.splitlines():
                        attr_info = ln.split()
                        attr_name = attr_info[0].strip()
                        attr_value = attr_info[1].strip()
                        attributes[attr_name] = attr_value
                    DEV[dev]['attr']=attributes

    return msg, DEV


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', default='all'),
            type=dict(type='str', default='all'),
            attr=dict(type='bool', default='yes'),
            dev=dict(type='dict', default={}),
        ),
        supports_check_mode=False
    )
    msg = ""
    dev_class = module.params['type']
    dev_name = module.params['name']
    attr = module.params['attr']
    DEV = module.params['dev']
    
    msg, DEV = load_dev(module, dev_name, dev_class, attr, DEV)

    module.exit_json(msg=msg, ansible_facts=dict(DEV=DEV))


if __name__ == '__main__':
    main()
