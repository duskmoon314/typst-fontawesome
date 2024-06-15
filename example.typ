#import "lib.typ": *

= typst-fontawesome

duskmoon314

https://github.com/duskmoon314/typst-fontawesome

A Typst library for Font Awesome 6.5.2 icons through the desktop fonts.

== Usage

=== Install the fonts

You can download the fonts from the official website: https://fontawesome.com/download

Or you can use the helper script to download the fonts and metadata:

`python helper.py -dd -v 6.5.2`

Here `-dd` means download and extract the zip file. You can use `-d` to only download the zip file.

After downloading the zip file, you can install the fonts depending on your OS.

==== Typst web app

You can simply upload the `otf` files to the web app and use them with this package.

==== Mac

You can double click the `otf` files to install them.

==== Windows

You can right click the `otf` files and select `Install`.

=== Import the library

==== Using the typst packages

You can install the library using the typst packages:

`#import "@preview/fontawesome:0.2.0": *`

==== Manually install

Copy all files start with `lib` to your project and import the library:

`#import "lib.typ": *`

There are three files:

- `lib.typ`: The main entrypoint of the library.
- `lib-impl.typ`: The implementation of `fa-icon`.
- `lib-gen.typ`: The generated icons.

I recommend renaming these files to avoid conflicts with other libraries.

=== Use the icons

You can use the `fa-icon` function to create an icon with its name:

```typst #fa-icon("chess-queen")``` #fa-icon("chess-queen")

Or you can use the `fa-` prefix to create an icon with its name:

```typst #fa-chess-queen()``` #fa-chess-queen() (This is equivalent to ```typst fa-icon().with("chess-queen")```)

You can also set `solid` to `true` to use the solid version of the icon:

```typst #fa-icon("chess-queen", solid: true)``` #fa-icon("chess-queen", solid: true)

If the icon only has a solid version, you can omit the `solid` parameter because the library automatically sets `solid` to `true` for these icons. For instance, the generated function for these icons would be like ```typst #fa-icon().with("arrow-trend-up", solid: true)```.

However, some icons (e.g. 0, 1, 2...) have a regular version that isn't mentioned in the metadata. In this case, you need to set `solid` to `false` to use the regular version.

==== Different sets

By default, the library uses two sets: `Free` and `Brands`.
That is, three font files are used:
- Font Awesome 6 Free (Also named as _Font Awesome 6 Free Regular_)
- Font Awesome 6 Free Solid
- Font Awesome 6 Brands

Due to some limitations of typst 0.11.0, the regular and solid versions are treated as different fonts.
In this library, `solid` is used to switch between the regular and solid versions.

To use `Pro` or other sets, you can pass the `font` parameter to the inner `text` function: \
```typst #fa-icon("github", font: "Font Awesome 6 Pro Solid")```

But you need to install the fonts first and take care of `solid` yourself.

==== Customization

The `fa-icon` function passes args to `text`, so you can customize the icon by passing parameters to it:

```typst #fa-icon("chess-queen", fill: blue)``` #fa-icon("chess-queen", fill: blue)

```typst #fa-chess-queen(size: 15pt)``` #fa-chess-queen(size: 15pt)

== Gallery

#include "gallery.typ"