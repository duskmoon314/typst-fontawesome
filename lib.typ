//! typst-fontawesome
//!
//! https://github.com/duskmoon314/typst-fontawesome

// Implementation of `fa-icon`
#import "lib-impl.typ": *

// Generated icons
#import "lib-gen.typ": *

// Re-export the `fa-icon` function
// The following doc comment is needed for lsp to show the documentation

/// Render a Font Awesome icon by its name or unicode
///
/// Parameters:
/// - `name`: The name of the icon
///   - This can be name in string or unicode of the icon
/// - `solid`: Whether to use the solid version of the icon
/// - `fa-icon-map`: The map of icon names to unicode
///   - Default is a map generated from FontAwesome metadata
///   - *Not recommended* You can provide your own map to override it
/// - `..args`: Additional arguments to pass to the `text` function
///
/// Returns: The rendered icon as a `text` element
#let fa-icon = fa-icon.with(fa-icon-map: fa-icon-map)

/// Render multiple Font Awesome icons together
///
/// Parameters:
/// - `icons`: The list of icons to render
///   - Each icon can be a string of the icon name or a tuple of the icon name and additional arguments
///   - For example, `"square"` or `("square", fill: red)`
/// - `box-args`: Additional arguments to pass to the `box` function
/// - `grid-args`: Additional arguments to pass to the `grid` function
/// - `fa-icon-args`: Additional arguments to pass to all `fa-icon` function
#let fa-stack(
  box-args: (:),
  grid-args: (:),
  fa-icon-args: (:),
  ..icons,
) = (
  context {
    let icons = icons.pos().map(icon => {
      if type(icon) == str {
        fa-icon(icon, ..fa-icon-args)
      } else {
        let (name, args) = icon
        fa-icon(name, ..fa-icon-args, ..args)
      }
    })

    // Get the maximum width of the icons
    let max-width = calc.max(
      ..icons.map(icon => {
        measure(icon).width
      }),
    )

    box(
      ..box-args,
      grid(
        align: center + horizon,
        columns: icons.len() * (max-width,),
        column-gutter: -max-width,
        rows: 1,
        ..grid-args,
        ..icons
      ),
    )
  }
)