#import "fontawesome.typ": *

= typst-fontawesome

duskmoon314

https://github.com/duskmoon314/typst-fontawesome

A Typst library for Font Awesome 6.4.0 icons through the desktop fonts.

== Usage

=== Install the fonts

You can download the fonts from the official website: https://fontawesome.com/download

Or you can use the helper script to download the fonts and metadata:

`python helper.py -dd -v 6.4.0`

Here `-dd` means download and extract the zip file. You can use `-d` to only download the zip file.

After downloading the zip file, you can install the fonts depending on your OS.

=== Import the library

Put the `fontawesome.typ` file in your project directory, and import it:

`#import "fontawesome.typ": *`

=== Use the icons

You can use the `fa-icon` function to create an icon with its name:

`fa-icon("chess-queen")()` #fa-icon("chess-queen")()

Or you can use the `fa-` prefix to create an icon with its name:

`fa-chess-queen()` #fa-chess-queen()

==== Customization

The `fa-icon` function is a curried `text`, so you can customize the icon by passing parameters to it:

`#fa-icon("chess-queen")(fill: blue)` #fa-icon("chess-queen")(fill: blue)

== Gallery

TODO
