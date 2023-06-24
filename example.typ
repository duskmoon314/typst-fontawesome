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

`fa-icon("chess-queen")` #fa-icon("chess-queen")

Or you can use the `fa-` prefix to create an icon with its name:

`fa-chess-queen()` #fa-chess-queen()

==== Different sets

By default, the library uses the free set. You can change it by passing the `fa-set` parameter to `fa-icon`:

`#fa-icon("github", fa-set: "Brands")` #fa-icon("github", fa-set: "Brands")

Or you can change the default set by changing the `FA_SET` state. Let's try with the github icon:

`#fa-icon("github")` #fa-icon("github")

`FA_SET.update("Brands")` #FA_SET.update("Brands")

`#fa-icon("github")` #fa-icon("github")

Reset the default set:

`FA_SET.update("Free")` #FA_SET.update("Free")

==== Customization

The `fa-icon` function passes args to `text`, so you can customize the icon by passing parameters to it:

`#fa-icon("chess-queen", fill: blue)` #fa-icon("chess-queen", fill: blue)

`#fa-chess-queen(size: 15pt)` #fa-chess-queen(size: 15pt)

== Gallery

TODO
