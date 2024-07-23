import argparse
import json
import zipfile
import urllib.request
import shutil
import os
import glob
import textwrap

parser = argparse.ArgumentParser(description="typst-fontawesome helper script")

parser.add_argument("-v", "--version", help="FontAwesome version", required=True)
parser.add_argument(
    "-o", "--output", help="Output dir (default: current dir .)", default="."
)
parser.add_argument(
    "-g",
    "--generate",
    help="Generate typst files (can be `lib`, `doc`)",
    default=["lib", "doc"],
)

API_URL = "https://api.fontawesome.com"
QUERY_TEMPLATE = """
query {{
    release (version: "{version}") {{
        icons {{
            id,
            unicode,
            familyStylesByLicense {{
                free {{ style }},
                pro {{ style }}
            }},
            aliases {{ names }}
        }}
    }}
}}
"""


def generate_lib(version, output):
    print(f"Generating typst lib for FontAwesome {version}")

    req = urllib.request.Request(
        API_URL,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        data=json.dumps({"query": QUERY_TEMPLATE.format(version=version)}).encode(
            "utf-8"
        ),
    )

    data = {}
    with urllib.request.urlopen(req) as response:
        data = json.load(response)

    LIB_PREAMBLE_TEMPLATE = """\
    #import "lib-impl.typ": fa-icon
    
    // Generated icon list of Font Aewsome {version}

    #let fa-icon-map = (
    """

    lib_preamble = textwrap.dedent(LIB_PREAMBLE_TEMPLATE).format(version=version)
    lib_file = os.path.join(output, "lib-gen.typ")

    icon_func_str = ""

    with open(lib_file, "w") as f:
        f.write(lib_preamble)

        for icon in data["data"]["release"]["icons"]:
            f.write(f'  "{icon["id"]}": "\\u{{{icon["unicode"]}}}",\n')
            icon_func_str += (
                f'#let fa-{icon["id"]} = fa-icon.with("\\u{{{icon["unicode"]}}}")\n'
            )

            if icon["aliases"]:
                for alias in icon["aliases"]["names"]:
                    f.write(f'  "{alias}": "\\u{{{icon["unicode"]}}}",\n')
                    icon_func_str += (
                        f'#let fa-{alias} = fa-icon.with("\\u{{{icon["unicode"]}}}")\n'
                    )

        f.write(")\n")
        f.write(icon_func_str)


def generate_gallery(version, output):
    print(f"Generating typst gallery for FontAwesome {version}")

    req = urllib.request.Request(
        API_URL,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        data=json.dumps({"query": QUERY_TEMPLATE.format(version=version)}).encode(
            "utf-8"
        ),
    )

    data = {}
    with urllib.request.urlopen(req) as response:
        data = json.load(response)

    gallery_file = os.path.join(output, "gallery.typ")

    with open(gallery_file, "w") as f:
        f.write('#import "lib.typ": *\n')

        f.write(
            # "#grid(columns: (20em, 3em, 3em, 3em), [typst code], [default], [solid], [`fa-icon` with text])\n"
            "#table(columns: (3fr, 1fr, 1fr, 2fr), stroke: none, table.header([typst code], [default], [solid], [`fa-icon` with text]),\n"
        )

        for icon in data["data"]["release"]["icons"]:
            f.write(
                f'```typst #fa-{icon["id"]}()```, fa-{icon["id"]}(), fa-{icon["id"]}(solid: true), fa-icon("{icon["id"]}"),\n'
            )

            if icon["aliases"]:
                for alias in icon["aliases"]["names"]:
                    f.write(
                        f'```typst #fa-{alias}()```, fa-{alias}(), fa-{alias}(solid: true), fa-icon("{alias}"),\n'
                    )

        f.write(")")


def main():
    args = parser.parse_args()

    if "lib" in args.generate:
        generate_lib(args.version, args.output)

    if "doc" in args.generate:
        generate_gallery(args.version, args.output)


if __name__ == "__main__":
    main()
