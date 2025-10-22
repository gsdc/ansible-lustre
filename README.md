gsdc.lustre
=========
* GSDC 시스템에서 Lustre 관련 패키지 및 커널모듈을 설치합니다.
* OS 버전별 설치하는 클라이언트 버전이 달라야 합니다. OS별로 현재 자동 설정되도록 하였습니다.
   

Requirements
------------
* kernel:되도록 최신버전의 커널로 업그레이드 및 재부팅 후에 설치할 것을 권장합니다.
* kernel-devel: DKMS 방식일 경우, 위 버전과 동일한 버전을 설치해야 합니다.


Role Variables
--------------
* type: Client or Server [ Current, only "client" is supported ]
* vendor: "cray"[default], "ddn"
* lustre_network: Lustre 스토리지와 연결될때 사용하는 네트워크 주소 예) 10.0.0.0/8

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
  become: yes
```
License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
