gsdc.lustre
=========

Install Lustre client kernel module for GSDC system

Requirements
------------

* kernel
* kernel-devel  

Role Variables
--------------

* type: Client or Server [ Current, only "client" is supported ]
* lustre_version: lustre package version on repository 

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:
-------
```bash
- hosts: my_nodes
  roles:
    - gsdc.lustre
  vars:
    type: "client"
    lustre_version: "2.15.4-1"
  become: yes
```
License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
