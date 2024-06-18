gsdc.lustre
=========
* GSDC 시스템에서 Lustre 관련 패키지 및 커널모듈을 설치합니다.
* OS 버전별 설치하는 클라이언트 버전이 달라야 합니다. OS별로 현재 자동 설정되도록 하였습니다.
   * Almalinux9.4 or higher => 2.15.63-1
     * Whamcloud 소스코드를 기반으로 생성하였으며 이후 변경 필요. minor 버전 업그레이드(9.4->9.5) 시 호환성 체크 필수!
   * CentOS7 => 2.15.0.4_rc2_cray_134_gb93242d-1 (DKMS 방식)

Requirements
------------
* kernel:되도록 최신버전의 커널로 업그레이드 및 재부팅 후에 설치할 것을 권장합니다.
* kernel-devel: DKMS 방식일 경우, 위 버전과 동일한 버전을 설치해야 합니다.


Role Variables
--------------
* type: Client or Server [ Current, only "client" is supported ]
     

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
