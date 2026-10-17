# Meitner

Meitner is a small interpreted programming language with a compact, whitespace-oriented syntax.

## Install

```bash
pipx install git+https://github.com/meitner-lang/meitner.git
# or
pip install git+https://github.com/meitner-lang/meitner.git
```

The `meitner` name on PyPI currently belongs to an unrelated SDK. This project uses the distribution name `meitner-lang`; its installed command remains `meitner`.

Run a program:

```bash
meitner program.meit
```

`meitner --tokens program.meit` prints the token list before running, and `meitner --version` prints the version.

## Example

```meitner
setvar [ score ] 10
addvar [ score ] 5

if [ score ] > 12 {
    print "high score"
}
else {
    print "keep going"
}

setvar [ i ] 0
loop 3 {
    addvar [ i ] 1
    print [ i ]
}
```

## The language at a glance

- **Values:** numbers (`10`), strings (`"hello"`), booleans (`true`, `false`), and variable references (`[ name ]`)
- **Variables:** `setvar [ name ] value` creates or replaces a variable
- **Output:** `print value`
- **Arithmetic:** `addvar`, `subvar`, `multvar`, `divvar` modify a variable in place (`divvar` is integer division)
- **Conditionals:** `if` with a boolean or a comparison (`=`, `!=`, `>`, `<`), plus optional `else`
- **Loops:** `loop <count> { ... }` and `loop forever { ... }`
- **Blocks:** `{ ... }` blocks can be nested
- **Comments:** `//` to the end of the line

Operators such as `=` and `>` must be separate from surrounding words. Brackets and braces are recognized even when adjacent to words. A `//` comment can begin immediately after a token.

> Meitner is early in development. These docs describe what the current interpreter implements.

## Documentation

See the [Language Reference](docs/LANGUAGE.md) for full syntax and behavior.

## Development

```bash
git clone https://github.com/meitner-lang/meitner.git
cd meitner
pip install -e . pytest
pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE).
