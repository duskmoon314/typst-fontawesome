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

    #let fa-icon-map = (
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

        icon_func_str = ""

        with open(icons_file, "r") as icons_f:
            icons_data = json.load(icons_f)

            for icon_name, icon_data in icons_data.items():
                # Check whether the icon only support solid style
                # styles contains "solid" but no "regular"
                solid = False
                if (
                    "solid" in icon_data["styles"]
                    and "regular" not in icon_data["styles"]
                ):
                    solid = True

                # Generate the icon line
                f.write(f'  "{icon_name}": "\\u{{{icon_data["unicode"]}}}",\n')
                icon_func_str += (
                    f'#let fa-{icon_name} = fa-icon.with("\\u{{{icon_data["unicode"]}}}")\n'
                    if not solid
                    else f'#let fa-{icon_name} = fa-icon.with("\\u{{{icon_data["unicode"]}}}", solid: true)\n'
                )

                # Generate the alias lines
                if "aliases" in icon_data:
                    if "names" in icon_data["aliases"]:
                        for alias_name in icon_data["aliases"]["names"]:
                            f.write(
                                f'  "{alias_name}": "\\u{{{icon_data["unicode"]}}}",\n'
                            )
                            icon_func_str += f"#let fa-{alias_name} = fa-icon.with(\"\\u{{{icon_data['unicode']}}}\")\n"

        f.write(")\n")
        f.write(icon_func_str)


def generate_gallery(version, output):
    print(f"Generating typst gallery for FontAwesome {version}")

    gallery_file = os.path.join(output, "gallery.typ")

    with open(gallery_file, "w") as f:
        f.write('#import "lib.typ": *\n')

        # Find the metadata/icons.json file with glob
        icons_file = glob.glob(
            os.path.join(output, "**/metadata/icons.json"), recursive=True
        )
        if len(icons_file) == 0:
            raise Exception("Cannot find metadata/icons.json")
        icons_file = icons_file[0]

        f.write(
            # "#grid(columns: (20em, 3em, 3em, 3em), [typst code], [default], [solid], [`fa-icon` with text])\n"
            "#table(columns: (3fr, 1fr, 1fr, 2fr), stroke: none, table.header([typst code], [default], [solid], [`fa-icon` with text]),\n"
        )

        with open(icons_file, "r") as icons_f:
            icons_data = json.load(icons_f)

            for icon_name, icon_data in icons_data.items():
                # Generate the icon line
                f.write(
                    # f'#grid(columns: (20em, 3em, 3em, 3em), ```typst #fa-{icon_name}()```, fa-{icon_name}(), fa-{icon_name}(solid: true)), fa-icon("{icon_name}")\n'
                    f'```typst #fa-{icon_name}()```, fa-{icon_name}(), fa-{icon_name}(solid: true), fa-icon("{icon_name}"),\n'
                )

                # Generate the alias lines
                if "aliases" in icon_data:
                    if "names" in icon_data["aliases"]:
                        for alias_name in icon_data["aliases"]["names"]:
                            f.write(
                                # f'#grid(columns: (20em, 3em, 3em, 3em), ```typst #fa-{alias_name}()```, fa-{alias_name}(), fa-{alias_name}(solid: true)), fa-icon("{alias_name}")\n'
                                f'```typst #fa-{alias_name}()```, fa-{alias_name}(), fa-{alias_name}(solid: true), fa-icon("{alias_name}"),\n'
                            )

        f.write(")")


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
