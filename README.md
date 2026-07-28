gsdc.lustre
=========
* GSDC 시스템에서 Lustre 관련 패키지 및 커널모듈을 설치합니다.
* OS 버전/vendor별로 설치하는 클라이언트 rpm이 다르며, `vars/os_<Distribution><Version>_<Vendor>.yml`
  파일로 조합별 설정을 관리합니다. `lustre_vendor` 변수로 어떤 조합을 쓸지 선택합니다.

Requirements
------------
* kernel: 되도록 최신 버전의 커널로 업그레이드 및 재부팅 후에 설치할 것을 권장합니다.
* kernel-devel: DKMS 방식일 경우, 위 커널 버전과 동일한 버전을 설치해야 합니다.

Role Variables
--------------
* `type`: Client or Server [ 현재 "client"만 지원 ]
* `lustre_vendor`: `"cray"`[default] | `"ddn"` | `"whamcloud"` — `vars/os_<Distribution><Version>_<Vendor>.yml`
  파일을 고르는 데 사용됩니다.
* `lustre_mgs_address`: Lustre MGS(관리 서버) 주소. 예) `192.168.1.10` (NID 형식
  `192.168.1.10@tcp0`도 허용됩니다). 이 주소로 실제 라우팅되는 인터페이스를
  `ip route get`으로 확인해 LNet 네트워크(`/etc/modprobe.d/lustre.conf`)로
  사용하므로 반드시 지정해야 합니다.
  * (호환용) 예전 `lustre_network`(서브넷 CIDR, 예: `192.168.0.0/16`) 변수를
    쓰던 클러스터는 `lustre_mgs_address`를 지정하지 않으면 그 서브넷의 첫
    주소(네트워크 주소 + 1)가 자동으로 사용됩니다.
* `lustre_dkms`: `false`[default] — `true`로 설정하면 커널 버전에 종속된 kmod 패키지
  (`client_packages`) 대신, 대상 `os_*.yml`에 정의된 DKMS 패키지 목록
  (`client_packages_dkms`)을 설치합니다. 대상 조합에 `client_packages_dkms`가
  정의되어 있어야 동작합니다.

패키지 설치 방식
----------------
`vars/os_<Distribution><Version>_<Vendor>.yml`에 `lustre_release_tag`가
정의되어 있으면, `tasks/client.yml`이 이 저장소의 GitHub Release
(`https://github.com/gsdc/ansible-lustre/releases/download/<lustre_release_tag>/<파일명>`)에서
`client_packages`(또는 `lustre_dkms: true`일 때 `client_packages_dkms`)를 직접
다운로드합니다. `lustre_release_tag`가 없으면 예전 방식대로 `files/<Distribution><Version>_<Vendor>/`
아래 로컬 파일을 사용합니다.

이 Release들은 `.github/workflows/build.yml`이 `srpm/*.build.yml` 빌드
가이드로부터 실제로 커널 모듈을 컴파일(kmod)하고 DKMS rpm까지 함께 빌드해서
자동으로 게시합니다. 빌드 방식/트리거(태그 push)에 대한 자세한 내용은
`srpm/README.md`를 참고하세요.

현재 지원하는 OS/vendor 조합
----------------------------
* AlmaLinux 9.7, 9.8: `cray`, `ddn` (release 기반)
* AlmaLinux 9.8: `whamcloud` (release 기반, `lustre/lustre-release` 최신 태그 자동 추적)
* Rocky 9.7, 9.8: `cray` (release 기반)

Dependencies
------------
A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Create ```install_lustre_role.yml```
```yaml
---
roles:
  - src: https://github.com/gsdc/ansible-lustre.git
    name: gsdc.lustre
```
Run install lustre role script using ansible-galaxy.
```bash
ansible-galaxy install -r install_lustre_role.yml --ignore-errors
```
Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:
-------
```bash
- hosts: my_nodes
  roles:
    - role: gsdc.lustre
      lustre_vendor: "cray"
      lustre_mgs_address: "192.168.1.10"
      # lustre_dkms: true   # 필요하면 커널 버전 종속 kmod 대신 DKMS 패키지 사용
  become: yes
```
License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
