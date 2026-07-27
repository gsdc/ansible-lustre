# srpm/

Lustre 소스 tarball(`*.tar.gz`, `make dist` 결과물 또는 벤더 릴리즈 소스)과, 이를 어떤
OS에서 어떻게 빌드해야 하는지 설명하는 "빌드 가이드"(`*.build.yml`)를 함께 보관하는
디렉토리입니다.

`.github/workflows/build.yml`이 이 디렉토리를 스캔해서 OS 버전별 컴파일 매트릭스를
자동으로 생성합니다. cray/ddn 벤더의 다운로드 URL에 의존하지 않고, 저장소에 커밋된
소스로 재현 가능하게 빌드하기 위한 목적입니다.

## 사용법

소스 tarball 하나당 같은 이름의 빌드 가이드 하나를 짝지어 추가합니다. tarball은
`lustre.spec`(kmod 빌드용) 및/또는 `lustre-dkms.spec.in`(DKMS 빌드용)을 포함한, 최상위에
`<name>-<version>/` 디렉토리 하나만 담고 있는 표준 Lustre 소스 배포본이어야 합니다
(`rpmbuild -tb`가 바로 사용할 수 있는 형태).

압축 해제된 소스 디렉토리(예: `lustre-2.14.0_ddn255/`)는 tarball의 내용을 그대로
풀어놓은 것이므로 저장소에는 tarball만 커밋하고, 압축 해제된 디렉토리는 커밋하지
않는 것을 권장합니다(수천 개 파일이 중복으로 git 히스토리에 쌓이는 것을 방지).

```
srpm/
  lustre-2.15.7.2_cray_39_g654b360-1.tar.gz
  lustre-2.15.7.2_cray_39_g654b360-1.build.yml
```

## 빌드 가이드 스키마 (`*.build.yml`)

```yaml
# 이 가이드가 대상으로 하는 소스 tarball 파일명 (같은 디렉토리 기준 상대경로)
source: lustre-2.15.7.2_cray_39_g654b360-1.tar.gz

# 이 소스로 빌드해야 하는 OS 목록
targets:
  - distribution: AlmaLinux
    version: "9.6"
    vendor: cray
  - distribution: AlmaLinux
    version: "9.7"
    vendor: cray

# true면 해당 target에는 lustre-client-dkms류(DKMS) 패키지만 있으면 된다는 뜻입니다.
# DKMS 패키지는 설치 시점에 대상 호스트에서 커널 모듈을 다시 빌드하므로,
# 커널 버전에 종속된 사전 컴파일이 필요 없습니다 -> workflow가 이 target의
# 컴파일 단계를 건너뛰고 "skip" 처리합니다.
# false면 kmod-lustre-client류(커널 버전 종속 사전 컴파일 바이너리)를 만들어야
# 한다는 뜻이며, workflow가 대상 배포판의 공식 GenericCloud 이미지를 QEMU/KVM으로
# 부팅한 뒤, 그 안에서 lustre.spec 기준으로 rpmbuild -tb를 실행해 컴파일하고
# modprobe로 커널 모듈 로드까지 검증합니다(컨테이너는 호스트 커널을 공유하므로
# 커널 모듈 빌드/로드 검증에 쓸 수 없어 VM을 사용합니다).
produces_dkms: true

# (선택) rpmbuild에 전달할 --with/--without 옵션. 생략하면 아래 기본값을 사용합니다.
rpmbuild_options: "--without servers --without zfs --with ldiskfs --without gss-keyring --without mpi --without o2ib"
```

## VM 이미지 미리 굽기 (bake-vm-image.yml)

`build.yml`이 매번 실행될 때마다 epel-release, CRB, Development Tools,
kernel-devel 등을 새로 설치하고 재부팅하는 건 낭비이므로, `.github/workflows/bake-vm-image.yml`을
`workflow_dispatch`로 수동 실행하면 이 준비를 미리 끝낸 VM 이미지를 만들어
`vm-image-<label>` (예: `vm-image-AlmaLinux9.8_ddn`) GitHub Release 애셋으로
올려둡니다.

`build.yml`은 실행될 때마다 먼저 해당 release가 있는지 확인해서, 있으면 그
이미지를 그대로 받아 패키지 설치/재부팅 단계를 건너뛰고 바로 소스 빌드만
수행합니다. 없으면 기존처럼 처음부터 준비합니다.

빌드 의존성 목록이나 커널이 바뀌어서 이미지를 새로 구워야 하면
`bake-vm-image.yml`을 다시 실행하면 됩니다(같은 태그에 `--clobber`로 덮어씀).
GitHub Release 애셋은 파일당 2GiB 제한이 있어서, 이미지가 이 이상 커지면
저장 방식을 바꿔야 할 수 있습니다.

## 참고

- `distribution`은 `AlmaLinux`, `Rocky`, `CentOS` 중 하나를 사용합니다(`vars/os_*.yml`
  파일명 규칙과 동일). 단, `produces_dkms: false`인 target을 실제로 컴파일하려면
  `.github/workflows/build.yml`의 "Locate cloud image URL" 단계에 해당 배포판의
  공식 GenericCloud 이미지 조회 로직이 있어야 합니다. 현재는 AlmaLinux만
  구현되어 있고, Rocky/CentOS는 필요해지면 같은 방식으로 추가해야 합니다.
- 같은 소스 tarball이 여러 OS/벤더 조합에 쓰인다면 `targets`에 여러 항목을 나열하면
  하나의 가이드로 여러 매트릭스 항목이 생성됩니다.
- 이 디렉토리는 현재 스캐폴딩만 되어 있는 상태입니다. 실제 `*.tar.gz`와
  `*.build.yml`을 추가해야 workflow의 compile 매트릭스가 채워집니다(비어 있으면
  compile job은 자동으로 skip됩니다).
