#!/usr/bin/env python

import os
import sys
import subprocess
import argparse

import yaml
from jinja2 import Template

# support Python 2 or 3
if sys.version_info[0] == 3:
    file_error = FileNotFoundError
else:
    file_error = IOError


def filehandle_if_exists_else_none(fname):
    try:
        return open(fname, "r")
    except file_error:
        return None


def open_compose_file(fname):
    if not fname:
        return filehandle_if_exists_else_none(
            "docker-compose.yaml"
        ) or filehandle_if_exists_else_none("docker-compose.yml")
    else:
        return filehandle_if_exists_else_none(fname)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        metavar="INPUT_FILE",
        type=open_compose_file,
        default="",
        help="Specify an alternate input compose file",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=argparse.FileType("r"),
        default="docker-compose.yml.jinja",
        help="Specify Jinja2 template file from which compose file will be generated. "
        "--template argument discards --file argument.",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT_FILE",
        type=argparse.FileType("w"),
        default="jinja-compose.yml",
        help="Specify an alternate output compose file (default: jinja-compose.yml)",
    )
    parser.add_argument(
        "-G",
        "--generate",
        action="store_true",
        help="Generate output compose file and exit, do not run docker-compose",
    )

    (args, extras) = parser.parse_known_args()

    if args.file is None and args.template is None:
        print("Missing docker-compose file.")
        sys.exit(1)

    if args.template is not None:
        content = Template(args.template.read()).render(ENV=os.environ)
        config = yaml.load(content, Loader=yaml.FullLoader)
    else:
        config = yaml.load(args.file, Loader=yaml.FullLoader)

    if config is None:
        raise RuntimeError("Compose file is empty")

    yaml.safe_dump(config, args.output, default_flow_style=False)

    if not args.generate:
        if sys.platform == "linux":
            try:
                from compose.cli.main import main as compose_main
            except ImportError:
                raise ImportError("Can't find docker compose.")

            sys.argv[:] = ["docker-compose", "-f", args.output.name] + extras
            compose_main()
        elif sys.platform == "darwin":
            process = subprocess.run(["docker-compose", "-f", args.output.name] + extras)


if __name__ == "__main__":
    main()
