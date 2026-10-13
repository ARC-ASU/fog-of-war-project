"""Create one private repository per student from this template, in the course organization.

    python staff/create_student_repos.py roster.csv --org <course-org> [--dry-run]

roster.csv has a header and two columns: asurite,github_username
Each student gets <org>/fow-<asurite>, private, generated from ARC-ASU/fog-of-war-project, and
an invitation with write ("push") access. Write access cannot change visibility or delete the
repository; organization owners (the staff) can read everything.

Requirements: the GitHub CLI (`gh`) logged in as an owner of the organization, and this template
repository marked as a template (Settings > Template repository).
"""
import argparse
import csv
import json
import subprocess
import sys

TEMPLATE = "ARC-ASU/fog-of-war-project"


def gh(*args, data=None):
    cmd = ["gh", "api", *args]
    if data is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(data) if data is not None else None,
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roster")
    ap.add_argument("--org", required=True)
    ap.add_argument("--prefix", default="fow-")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(args.roster)))
    for row in rows:
        asurite, user = row["asurite"].strip(), row["github_username"].strip()
        name = f"{args.prefix}{asurite}"
        print(f"{args.org}/{name}  <-  {user}")
        if args.dry_run:
            continue
        code, out, err = gh(f"repos/{args.org}/{name}")
        if code != 0:
            code, out, err = gh("-X", "POST", f"repos/{TEMPLATE}/generate",
                                data={"owner": args.org, "name": name, "private": True,
                                      "description": f"CSE 598 Fog-of-War project: {asurite}"})
            if code != 0:
                print("  could not create:", err.strip(), file=sys.stderr)
                continue
        code, out, err = gh("-X", "PUT", f"repos/{args.org}/{name}/collaborators/{user}",
                            data={"permission": "push"})
        print("  invited" if code == 0 else f"  invite failed: {err.strip()}")


if __name__ == "__main__":
    main()
