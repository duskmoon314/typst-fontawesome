import argparse
import json
import zipfile
import urllib.request
import shutil
import os
import glob
import textwrap

parser = argparse.ArgumentParser(description="typst-fontawesome helper script")

parser.add_argument(
    "-d",
    "--download",
    help="Download FontAwesome fonts and metadata (occur two times to extract the zip file)",
    action="count",
    default=0,
)
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


def download(version, output, extract=False):
    ZIP_LINK_TEMPLATE = (
        "https://use.fontawesome.com/releases/v{}/fontawesome-free-{}-desktop.zip"
    )
    zip_link = ZIP_LINK_TEMPLATE.format(version, version)

    print(f"Downloading FontAwesome {version} metadata from {zip_link}")

    zip_file = os.path.join(output, "fontawesome.zip")

    # Download the zip file to the output directory
    req = urllib.request.Request(zip_link, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        with open(zip_file, "wb") as f:
            shutil.copyfileobj(response, f)

    if extract:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(output)


def generate_lib(version, output):
    print(f"Generating typst lib for FontAwesome {version}")

    LIB_PREAMBLE_TEMPLATE = """\
    #import "lib-impl.typ": fa-icon
    
    // Generated icon list of Font Aewsome {version}

    """

    lib_preamble = textwrap.dedent(LIB_PREAMBLE_TEMPLATE).format(version=version)

    lib_file = os.path.join(output, "lib-gen.typ")

    with open(lib_file, "w") as f:
        f.write(lib_preamble)

        # Find the metadata/icons.json file with glob
        icons_file = glob.glob(
            os.path.join(output, "**/metadata/icons.json"), recursive=True
        )
        if len(icons_file) == 0:
            raise Exception("Cannot find metadata/icons.json")
        icons_file = icons_file[0]

        with open(icons_file, "r") as icons_f:
            icons_data = json.load(icons_f)

            for icon_name, icon_data in icons_data.items():
                # Generate the icon line
                f.write(
                    f"#let fa-{icon_name} = fa-icon.with(\"\\u{{{icon_data['unicode']}}}\")\n"
                )

                # Generate the alias lines
                if "aliases" in icon_data:
                    if "names" in icon_data["aliases"]:
                        for alias_name in icon_data["aliases"]["names"]:
                            f.write(
                                f"#let fa-{alias_name} = fa-icon.with(\"\\u{{{icon_data['unicode']}}}\")\n"
                            )


def generate_gallery(version, output):
    print(f"Generating typst gallery for FontAwesome {version}")

    gallery_file = os.path.join(output, "gallery.typ")

    with open(gallery_file, "w") as f:
        f.write("#import \"lib.typ\": *\n")

        # Find the metadata/icons.json file with glob
        icons_file = glob.glob(
            os.path.join(output, "**/metadata/icons.json"), recursive=True
        )
        if len(icons_file) == 0:
            raise Exception("Cannot find metadata/icons.json")
        icons_file = icons_file[0]

        with open(icons_file, "r") as icons_f:
            icons_data = json.load(icons_f)

            for icon_name, icon_data in icons_data.items():
                # Generate the icon line
                f.write(
                    f"#grid(columns: (20em, 10em, 3em), `#fa-{icon_name}()`, fa-{icon_name}())\n"
                )

                # Generate the alias lines
                if "aliases" in icon_data:
                    if "names" in icon_data["aliases"]:
                        for alias_name in icon_data["aliases"]["names"]:
                            f.write(
                                f"#grid(columns: (20em, 10em, 3em), `#fa-{alias_name}()`, fa-{alias_name}())\n"
                            )


def main():
    args = parser.parse_args()

    if args.download > 0:
        download(args.version, args.output, args.download > 1)

    if "lib" in args.generate:
        generate_lib(args.version, args.output)

    if "doc" in args.generate:
        generate_gallery(args.version, args.output)


if __name__ == "__main__":
    main()
