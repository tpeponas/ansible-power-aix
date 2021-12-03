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
- List and reports details about defined AIX Logical Volume Manager (LVM) components such as
  Physical volumes, Logical volumes and Volume groups in Ansible facts.
version_added: '2.9'
requirements:
- AIX >= 7.1 TL3
- Python >= 2.7
options:
  name:
    description:
    - Specifies the name of a LVM component.
    type: str
    default: 'all'
  component:
    description:
    - Specifies the type of LVM component to report information.
      A(pv) specifies physical volume.
      A(lv) specifies logical volume.
      A(vg) specifies volume group.
      C(all) specifies all previous LVM components to be reported.
    type: str
    choices: [pv, lv, vg, all]
    default: 'all'
  lvm:
    description:
    - Users can provide the existing LVM facts to which the queried facts should be updated.
      If not specified, the LVM facts in the ansible_facts will be replaced.
    type: dict
    default: {}

'''

EXAMPLES = r'''
- name: Gather all lvm facts
  lvm_facts:
- name: Gather VG facts
  lvm_facts:
    name: all
    component: vg
- name: Update PV facts to existing LVM facts
  lvm_facts:
    name: all
    component: pv
    lvm: "{{ ansible_facts.LVM }}"
- name: Gather LV facts
  lvm_facts:
    name: all
    component: lv
'''

RETURN = r'''
ansible_facts:
  description:
  - Facts to add to ansible_facts about the LVM components on the system.
  returned: always
  type: complex
  contains:
    lvm:
      description:
      - Contains a list of VGs, PVs and LVs.
      returned: success
      type: dict
      elements: dict
      contains:
        VGs:
          description:
          - Contains the list of volume groups on the system.
          returned: success
          type: dict
          elements: dict
          contains:
            name:
              description:
              - Volume Group name.
              returned: always
              type: str
              sample: "rootvg"
            vg_state:
              description:
              - State of the Volume Group.
              returned: always
              type: str
              sample: "active"
            num_lvs:
              description:
              - Number of logical volumes.
              returned: always
              type: str
              sample: "2"
            num_pvs:
              description:
              - Number of physical volumes.
              returned: always
              type: str
              sample: "2"
            total_pps:
              description:
              - Total number of physical partitions within the volume group.
              returned: always
              type: str
              sample: "952"
            free_pps:
              description:
              - Number of physical partitions not allocated.
              returned: always
              type: str
              sample: "100"
            pp_size:
              description:
              - Size of each physical partition.
              returned: always
              type: str
              sample: "64 megabyte (s)"
            size_g:
              description:
              - Total size of the volume group in gigabytes.
              returned: always
              type: str
              sample: "18.99"
            free_g:
              description:
              - Free space of the volume group in gigabytes.
              returned: always
              type: str
              sample: "10.6"
        PVs:
          description:
          - Contains a list of physical volumes on the system.
          returned: success
          type: dict
          elements: dict
          contains:
            name:
              description:
              - PV name
              returned: always
              type: str
              sample: "hdisk0"
            vg:
              description:
              - Volume group to which the physical volume has been assigned.
              returned: always
              type: str
              sample: "rootvg"
            pv_state:
              description:
              - Physical volume state.
              returned: always
              type: str
              sample: "active"
            total_pps:
              description:
              - Total number of physical partitions in the physical volume.
              returned: always
              type: str
              sample: "476"
            free_pps:
              description:
              - Number of free physical partitions in the physical volume.
              returned: always
              type: str
              sample: "130"
            pp_size:
              description:
              - Size of each physical partition.
              returned: always
              type: str
              sample: "64 megabyte (s)"
            size_g:
              description:
              - Total size of the physical volume in gigabytes.
              returned: always
              type: str
              sample: "18.99"
            free_g:
              description:
              - Free space of the physical volume in gigabytes.
              returned: always
              type: str
              sample: "10.6"
        LVs:
          description:
          - Contains a list of logical volumes on the system.
          returned: success
          type: dict
          elements: dict
          contains:
            name:
              description:
              - Logical volume name.
              returned: always
              type: str
              sample: "hd1"
            vg:
              description:
              - Volume group to which the Logical Volume belongs to.
              returned: always
              type: str
              sample: "rootvg"
            lv_state:
              description:
              - Logical Volume state.
              returned: always
              type: str
              sample: "active"
            type:
              description:
              - Logical volume type.
              returned: always
              type: str
              sample: "jfs2"
            LPs:
              description:
              - Total number of logical partitions in the logical volume.
              returned: always
              type: str
              sample: "476"
            PPs:
              description:
              - Total number of physical partitions in the logical volume.
              returned: always
              type: str
              sample: "130"
            PVs:
              description:
              - Number of physical volumes used by the logical volume.
              returned: always
              type: str
              sample: "2"
            mount_point:
              description:
              - File system mount point for the logical volume, if applicable.
              returned: always
              type: str
              sample: "/home"
'''

from ansible.module_utils.basic import AnsibleModule
import re

def load_dev(module, dev_name, dev_class, get_attr, DEV):
    """
    Get the details for the specified Dev or all
    arguments:
        module  (dict): Ansible module argument spec.
        name     (str): Device name.
        DEV     (dict): DEV facts.
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
            if (not get_attr):
                return msg,DEV

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
            type=dict(type='str', default='all', choices=['disk', 'adapter', 'all']),
            attr=dict(type='bool', default='yes'),
            dev=dict(type='dict', default={}),
        ),
        supports_check_mode=False
    )
    msg = ""
    dev_class = module.params['type']
    dev_name = module.params['name']
    DEV = module.params['lvm']
    
    msg, DEV = load_dev(module, dev_name, dev_class, DEV)

    module.exit_json(msg=msg, ansible_facts=dict(DEV=DEV))


if __name__ == '__main__':
    main()
