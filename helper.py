import argparse
import json
import urllib.request
import os
from typing import List, Set, Dict, Tuple

parser = argparse.ArgumentParser(description="typst-fontawesome helper script")

parser.add_argument(
    "-v",
    "--version",
    help="FontAwesome version. (Example: -v 6.7.2,7.0.0)",
    required=True,
)
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


def fetch_icons(version: str) -> Set[Tuple[str, str]]:
    """
    Fetch icons from FontAwesome API for a specific version.

    Args:
        version: The version of FontAwesome to fetch icons for.

    Returns:
        Set: A set of tuples containing icon IDs and their corresponding unicode characters.
    """

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

    icon_unicode_set = set()
    for icon in data["data"]["release"]["icons"]:
        icon_unicode_set.add((icon["id"], icon["unicode"]))

        if icon["aliases"]:
            for alias in icon["aliases"]["names"]:
                icon_unicode_set.add((alias, icon["unicode"]))

    return icon_unicode_set


def map_icons(versions: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Map icons from multiple FontAwesome versions to their unicode characters.

    Args:
        versions: A list of FontAwesome versions to map icons from.

    Returns:
        Dict: A dictionary where keys are version strings and values are lists of tuples
              containing icon IDs and their corresponding unicode characters.
    """
    origin_icon_sets = []
    for version in versions:
        icon_set = fetch_icons(version)
        major_version = int(version.split(".")[0])
        origin_icon_sets.append((major_version, icon_set))

    icon_unicodes = {}

    # Collect all icon unicodes across versions
    # If an icon has the same unicode in different versions, it will be marked as common
    # If an icon has different unicodes in different versions, it will be marked as conflict

    for version, icon_set in origin_icon_sets:
        for icon_id, unicode in icon_set:
            if icon_id not in icon_unicodes:
                icon_unicodes[icon_id] = set()
            icon_unicodes[icon_id].add((version, unicode))

    for icon_id, unicodes in icon_unicodes.items():
        unicode_set = set(unicode for _, unicode in unicodes)
        if len(unicode_set) == 1:
            icon_unicodes[icon_id] = set()
            icon_unicodes[icon_id].add(("common", unicode_set.pop()))

    icon_map = {}
    common = [
        (icon_id, unicodes.pop()[1])
        for icon_id, unicodes in icon_unicodes.items()
        if len(unicodes) == 1
    ]

    icon_map["common"] = common

    conflict = [
        (icon_id, unicodes)
        for icon_id, unicodes in icon_unicodes.items()
        if len(unicodes) > 1
    ]

    for icon_id, unicodes in conflict:

        for version, unicode in unicodes:
            if version not in icon_map:
                icon_map[version] = []
            icon_map[version].append((icon_id, unicode))

    for _, map in icon_map.items():
        map.sort(key=lambda x: (x[1], x[0]))  # Sort by unicode first, then by icon_id

    return icon_map


def generate_lib(icon_maps: Dict[str, List[Tuple[str, str]]], output: str):
    """
    Generate typst library files for FontAwesome icons.

    Args:
        icon_maps: A dictionary containing icon maps for different FontAwesome versions.
        output: The output directory where the typst files will be generated.
    """

    lib_map_file = os.path.join(output, "lib-gen-map.typ")
    lib_func_file = os.path.join(output, "lib-gen-func.typ")

    with open(lib_map_file, "w") as f:
        f.write("// Generated icon maps of Font Awesome\n\n")

        icon_func_str = ""

        f.write("// Common icons\n")
        f.write("#let fa-icon-map-common = (\n")
        for icon in icon_maps["common"]:
            icon_id, unicode_char = icon
            f.write(f'  "{icon_id}": "\\u{{{unicode_char}}}",\n')
            icon_func_str += (
                f'#let fa-{icon_id} = fa-icon.with("\\u{{{unicode_char}}}")\n'
            )
        f.write(")\n\n")

        del icon_maps["common"]

        latest_version = max(icon_maps.keys())

        for version, icons in sorted(icon_maps.items()):
            f.write(f"// Version: {version}\n")
            f.write(f"#let fa-icon-map-{version} = (\n")
            for icon_id, unicode_char in icons:
                f.write(f'  "{icon_id}": "\\u{{{unicode_char}}}",\n')
                icon_func_str += f'#let fa-{icon_id}-{version} = fa-icon.with("\\u{{{unicode_char}}}")\n'
                if version == latest_version:
                    icon_func_str += (
                        f'#let fa-{icon_id} = fa-icon.with("\\u{{{unicode_char}}}")\n'
                    )
            f.write(")\n\n")

        f.write("#let fa-icon-map-version = (\n")
        for version in sorted(icon_maps.keys()):
            f.write(f'  "{version}": fa-icon-map-{version},\n')
        f.write(")\n")

    with open(lib_func_file, "w") as f:
        f.write('#import "lib-impl.typ": fa-icon\n\n')
        f.write("// Generated icon functions of Font Awesome\n\n")
        f.write(icon_func_str)


def generate_gallery(icon_maps: Dict[str, List[Tuple[str, str]]], output: str):
    """
    Generate a typst gallery file for FontAwesome icons.

    Args:
        icon_maps: A dictionary containing icon maps for different FontAwesome versions.
        output: The output directory where the typst gallery file will be generated.
    """

    gallery_file = os.path.join(output, "gallery.typ")

    with open(gallery_file, "w") as f:
        f.write('#import "lib.typ": *\n')

        f.write(
            "#table(\n  columns: (3fr, 1fr, 1fr, 2fr),\n  stroke: none,\n  table.header([typst code], [default], [solid], [`fa-icon` with text]),\n"
        )

        for icon in icon_maps["common"]:
            icon_id, _unicode_char = icon
            f.write(
                f'  ```typst #fa-{icon_id}()```, fa-{icon_id}(), fa-{icon_id}(solid: true), fa-icon("{icon_id}"),\n'
            )

        del icon_maps["common"]

        for version, icons in sorted(icon_maps.items()):
            for icon_id, _unicode_char in icons:
                f.write(
                    f'  ```typst #fa-{icon_id}-{version}()```, fa-{icon_id}-{version}(), fa-{icon_id}-{version}(solid: true), fa-icon("{icon_id}-{version}"),\n'
                )

        f.write(")")


def main():
    args = parser.parse_args()

    versions = args.version.split(",")

    print(f"Generating typst-fontawesome for versions: {versions}")

    icon_maps = map_icons(versions)

    # with open(os.path.join(args.output, "icon-maps.json"), "w") as f:
    #     json.dump(icon_maps, f, indent=2)

    if "lib" in args.generate:
        generate_lib(icon_maps.copy(), args.output)

    if "doc" in args.generate:
        generate_gallery(icon_maps.copy(), args.output)


if __name__ == "__main__":
    main()
