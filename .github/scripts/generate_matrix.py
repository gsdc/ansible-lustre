#!/usr/bin/env python3
"""Build the GitHub Actions compile matrix from srpm/*.build.yml guides.

Each build guide describes one source rpm and the OS/vendor targets it
should be compiled for. Targets whose package is DKMS-based don't need a
kernel-specific pre-compile (the module is rebuilt on the target host at
install time), so they're marked to be skipped rather than compiled.
"""
import glob
import json
import os
import sys

import yaml

IMAGE_MAP = {
    "AlmaLinux": "almalinux",
    "Rocky": "rockylinux",
    "CentOS": "centos",
}

DEFAULT_RPMBUILD_OPTIONS = (
    "--without servers --without zfs --with ldiskfs "
    "--without gss-keyring --without mpi --without o2ib"
)


def image_for(distribution, version):
    name = IMAGE_MAP.get(distribution)
    if not name:
        raise ValueError(f"Unknown distribution: {distribution}")
    major = version.split(".")[0]
    return f"{name}:{major}"


def load_guide(guide_path):
    with open(guide_path) as f:
        guide = yaml.safe_load(f) or {}

    source_name = guide.get("source")
    if not source_name:
        print(f"::error file={guide_path}::'source' key is required", file=sys.stderr)
        sys.exit(1)

    source_path = os.path.join("srpm", source_name)
    if not os.path.isfile(source_path):
        print(f"::error file={guide_path}::source file not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    targets = guide.get("targets") or []
    if not targets:
        print(f"::error file={guide_path}::'targets' must list at least one OS", file=sys.stderr)
        sys.exit(1)

    return guide, source_name, targets


def main():
    guides = sorted(glob.glob("srpm/*.build.yml"))
    include = []

    for guide_path in guides:
        guide, source_name, targets = load_guide(guide_path)
        produces_dkms = bool(guide.get("produces_dkms", False))
        rpmbuild_options = guide.get("rpmbuild_options", DEFAULT_RPMBUILD_OPTIONS)

        for target in targets:
            distribution = target["distribution"]
            version = str(target["version"])
            vendor = target.get("vendor", "")
            include.append({
                "guide": guide_path,
                "source": source_name,
                "distribution": distribution,
                "version": version,
                "vendor": vendor,
                "image": image_for(distribution, version),
                "produces_dkms": produces_dkms,
                "rpmbuild_options": rpmbuild_options,
                "label": f"{distribution}{version}_{vendor}".strip("_"),
            })

    matrix = {"include": include}
    has_jobs = "true" if include else "false"

    lines = [f"matrix={json.dumps(matrix)}", f"has_jobs={has_jobs}"]
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            for line in lines:
                f.write(line + "\n")
    else:
        for line in lines:
            print(line)

    to_compile = [i for i in include if not i["produces_dkms"]]
    to_skip = [i for i in include if i["produces_dkms"]]
    print(
        f"Discovered {len(include)} target(s) from {len(guides)} build guide(s): "
        f"{len(to_compile)} to compile, {len(to_skip)} to skip (DKMS-only)."
    )


if __name__ == "__main__":
    main()
