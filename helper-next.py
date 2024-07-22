import argparse
import json
import os
import textwrap
from urllib import request

parser = argparse.ArgumentParser(description="typst-fontawesome helper script")

parser.add_argument("-v", "--version", help="FontAwesome version", required=True)
parser.add_argument(
    "-o", "--output", help="Output dir (default: current dir .)", default="."
)


def metadata(version, output):
    # Using FontAwesome GraphQL API to get the metadata

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

    req = request.Request(
        API_URL,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        data=json.dumps({"query": QUERY_TEMPLATE.format(version=version)}).encode(
            "utf-8"
        ),
    )

    data = {}

    with request.urlopen(req) as response:
        data = json.load(response)

        # print(data)
        # print(len(data["data"]["release"]["icons"]))

        # # dump to test.json
        # with open("test.json", "w") as f:
        #     json.dump(data, f, indent=2)

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


def main():
    args = parser.parse_args()

    metadata(args.version, args.output)


if __name__ == "__main__":
    main()
