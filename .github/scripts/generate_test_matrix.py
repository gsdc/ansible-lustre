#!/usr/bin/env python3
"""Build the GitHub Actions test matrix from vars/os_*.yml files.

Each os_<Distribution><Version>_<Vendor>.yml describes one released
OS/vendor combination the ansible role supports (lustre_release_tag +
client_packages / client_packages_dkms). This generates one matrix entry per
combination per install mode (kmod vs DKMS), so test-role.yml can boot a real
VM, run the role's tasks/client.yml against it with that lustre_vendor +
lustre_dkms, and verify the shipped rpm actually installs and modprobes.
"""
import argparse
import glob
import json
import os
import re
import sys

VARS_FILE_RE = re.compile(r"^os_([A-Za-z]+)([0-9]+(?:\.[0-9]+)*)_([A-Za-z0-9]+)\.yml$")


def discover_targets():
    targets = []
    for path in sorted(glob.glob("vars/os_*.yml")):
        name = os.path.basename(path)
        m = VARS_FILE_RE.match(name)
        if not m:
            print(f"::warning file={path}::filename doesn't match os_<Distribution><Version>_<Vendor>.yml, skipping", file=sys.stderr)
            continue
        distribution, version, vendor = m.groups()
        targets.append({
            "distribution": distribution,
            "version": version,
            "vendor": vendor,
            "label": f"{distribution}{version}_{vendor}",
        })
    return targets


def filter_by_label(targets, label):
    return [t for t in targets if t["label"] == label]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filter-label",
        default=None,
        help="Only include the target whose label matches exactly (e.g. 'AlmaLinux9.8_cray').",
    )
    parser.add_argument(
        "--dkms-modes",
        default="false,true",
        help="Comma-separated lustre_dkms values to expand each target into (default: 'false,true').",
    )
    args = parser.parse_args()

    targets = discover_targets()

    if args.filter_label:
        before = len(targets)
        targets = filter_by_label(targets, args.filter_label)
        print(f"Filtered {before} target(s) down to {len(targets)} matching label '{args.filter_label}'.")

    dkms_modes = [v.strip().lower() == "true" for v in args.dkms_modes.split(",") if v.strip()]

    include = []
    for target in targets:
        for dkms in dkms_modes:
            include.append({
                **target,
                "dkms": dkms,
                "test_id": f"{target['label']}_{'dkms' if dkms else 'kmod'}",
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

    print(f"Discovered {len(include)} test job(s) from {len(targets)} OS/vendor combination(s).")


if __name__ == "__main__":
    main()
