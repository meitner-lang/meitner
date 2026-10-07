# Changelog

All notable changes to Meitner are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While the version is below 1.0, minor versions may include breaking changes.

## [0.2.0] - Unreleased

### Added

- Quoted string literals
- Integer literals and bare-word values
- Boolean literals (`true` and `false`)
- Mutable variables with `setvar`
- Variable references with `[ name ]`
- `print` for strings, numbers, booleans, and variables
- Integer arithmetic with `addvar`, `subvar`, `multvar`, and `divvar`
- Conditional execution with `if`
- `else` blocks
- Comparison operators `=`, `!=`, `>`, and `<`
- Brace-delimited blocks, including nested blocks
- `loop <count> { ... }` and `loop forever { ... }`
- `//` line comments
- Command-line interface: `meitner <file.meit>`, with `--tokens` and `--version` flags

### Known limitations

- No functions, function arguments, or return values
- No lists, arrays, maps, or structures
- No general expressions or operator precedence
- No string escapes or string interpolation
- No local block scope; all variables are global
- No imports or user-defined types

## [0.1.0]

Initial development version. Not published.
