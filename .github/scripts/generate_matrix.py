#!/usr/bin/env python3
"""Build the GitHub Actions compile matrix from srpm/*.build.yml guides.

Each build guide describes one source rpm and the OS/vendor targets it
should be compiled for. Targets whose package is DKMS-based don't need a
kernel-specific pre-compile (the module is rebuilt on the target host at
install time), so they're marked to be skipped rather than compiled.
"""
import argparse
import glob
import json
import os
import sys

import yaml

DEFAULT_RPMBUILD_OPTIONS = (
    "--without servers --without zfs --with ldiskfs "
    "--without gss-keyring --without mpi --without o2ib"
)


def load_guide(guide_path):
    with open(guide_path) as f:
        guide = yaml.safe_load(f) or {}

    source = guide.get("source")
    if not source:
        print(f"::error file={guide_path}::'source' key is required", file=sys.stderr)
        sys.exit(1)

    srpm_path_in_zip = ""

    if isinstance(source, str):
        # Existing mode: a source tarball committed under srpm/.
        source_path = os.path.join("srpm", source)
        if not os.path.isfile(source_path):
            print(f"::error file={guide_path}::source file not found: {source_path}", file=sys.stderr)
            sys.exit(1)
        source_type = "tarball"
        source_name = source
        github_ref = ""
    elif isinstance(source, dict) and source.get("github_ref"):
        # Whamcloud mode: build straight from github.com/lustre/lustre-release
        # at the given tag/branch, no tarball needs to be committed.
        github_ref = str(source["github_ref"])
        source_type = "github"
        source_name = f"lustre-whamcloud-{github_ref}.tar.gz"
    elif isinstance(source, dict) and source.get("zip") and source.get("srpm_path"):
        # Vendor .src.rpm shipped inside a zip archive (e.g. Cray/HPE releases).
        zip_name = source["zip"]
        zip_path = os.path.join("srpm", zip_name)
        if not os.path.isfile(zip_path):
            print(f"::error file={guide_path}::zip file not found: {zip_path}", file=sys.stderr)
            sys.exit(1)
        source_type = "srpm_zip"
        source_name = zip_name
        github_ref = ""
        srpm_path_in_zip = str(source["srpm_path"])
    else:
        print(
            f"::error file={guide_path}::'source' must be a tarball filename (string), "
            "a mapping with 'github_ref' (e.g. {{github_ref: 2.15.6}}), or a mapping with "
            "'zip'/'srpm_path' (e.g. {{zip: foo.zip, srpm_path: rpmbuild/foo.src.rpm}})",
            file=sys.stderr,
        )
        sys.exit(1)

    targets = guide.get("targets") or []
    if not targets:
        print(f"::error file={guide_path}::'targets' must list at least one OS", file=sys.stderr)
        sys.exit(1)

    return guide, source_name, source_type, github_ref, srpm_path_in_zip, targets


def dedupe_by_os_key(include):
    """Keep only the first entry per os_key (distribution+version, no vendor).

    Used for the VM-image bake matrix: the base OS image (packages,
    kernel-devel, reboot) is identical regardless of vendor - only the
    Lustre source built on top of it differs - so AlmaLinux9.8_ddn,
    AlmaLinux9.8_cray and AlmaLinux9.8_whamcloud should all share one baked
    image instead of each getting their own.
    """
    seen = set()
    deduped = []
    for entry in include:
        if entry["os_key"] in seen:
            continue
        seen.add(entry["os_key"])
        deduped.append(entry)
    return deduped


def filter_by_label_prefix(include, prefix):
    """Keep only entries whose label is exactly `prefix` or `prefix_<vendor>`.

    Used when a build is triggered by an OS-targeted tag (e.g.
    "AlmaLinux_9.8_v20260727") that names a distribution+version but not a
    vendor, so every vendor variant of that OS/version should still match.
    """
    return [
        entry for entry in include
        if entry["label"] == prefix or entry["label"].startswith(prefix + "_")
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dedupe-by-os",
        action="store_true",
        help="Collapse targets that share the same distribution+version (any vendor) into one entry.",
    )
    parser.add_argument(
        "--filter-label-prefix",
        default=None,
        help="Only include targets whose label is this distribution+version (e.g. 'AlmaLinux9.8'), any vendor.",
    )
    args = parser.parse_args()

    guides = sorted(glob.glob("srpm/*.build.yml"))
    include = []

    for guide_path in guides:
        guide, source_name, source_type, github_ref, srpm_path_in_zip, targets = load_guide(guide_path)
        produces_dkms = bool(guide.get("produces_dkms", False))
        rpmbuild_options = guide.get("rpmbuild_options", DEFAULT_RPMBUILD_OPTIONS)

        for target in targets:
            distribution = target["distribution"]
            version = str(target["version"])
            vendor = target.get("vendor", "")
            include.append({
                "guide": guide_path,
                "source": source_name,
                "source_type": source_type,
                "github_ref": github_ref,
                "srpm_path_in_zip": srpm_path_in_zip,
                "distribution": distribution,
                "version": version,
                "vendor": vendor,
                "produces_dkms": produces_dkms,
                "rpmbuild_options": rpmbuild_options,
                "label": f"{distribution}{version}_{vendor}".strip("_"),
                "os_key": f"{distribution}{version}",
            })

    if args.filter_label_prefix:
        before = len(include)
        include = filter_by_label_prefix(include, args.filter_label_prefix)
        print(f"Filtered {before} target(s) down to {len(include)} matching label prefix '{args.filter_label_prefix}'.")

    if args.dedupe_by_os:
        before = len(include)
        include = dedupe_by_os_key(include)
        if before != len(include):
            print(f"Deduped {before} target(s) down to {len(include)} unique OS/version(s).")

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
