# Meitner

Meitner is a small interpreted programming language with a compact, whitespace-oriented syntax.

The current language includes:

- quoted string literals
- integer-like literal values
- mutable variables
- bracketed variable references
- printing
- integer addition into an existing variable
- conditional execution
- brace-delimited conditional blocks
- equality, inequality, greater-than, and less-than comparisons

> Meitner is early in development. This README documents the language implemented by the current interpreter, not planned or proposed syntax.

## Example

```meitner
setvar [ score ] 10
print [ score ]
addvar [ score ] 5

if 15 = 15 {
    print "score updated"
}
```

## Language overview

### Strings

String literals are enclosed in double quotes:

```meitner
"hello"
"Meitner"
```

Escape sequences are not currently implemented, so a double quote terminates the string.

### Variables

Create or replace a variable with `setvar`:

```meitner
setvar [ name ] "Meitner"
setvar [ count ] 10
```

Variable references use square brackets in language features that currently support lookup:

```meitner
print [ name ]
```

`setvar` is mutable: assigning an already-existing name replaces its current value.

### Printing

Print a quoted string:

```meitner
print "hello"
```

Print a variable:

```meitner
print [ name ]
```

### Adding to a variable

`addvar` converts the variable's current value and the supplied value to integers, adds them, and stores the integer result back in the variable:

```meitner
setvar [ count ] 10
addvar [ count ] 5
print [ count ]
```

After the addition, `count` contains the integer value `15`.

### Conditionals

Conditional blocks use `if`, two literal operands, a comparison operator, and a brace-delimited block:

```meitner
if 4 > 2 {
    print "yes"
}
```

Currently implemented comparison operators are:

| Operator | Meaning |
| --- | --- |
| `=` | equal |
| `!=` | not equal |
| `>` | greater than |
| `<` | less than |

`>` and `<` convert both operands to integers before comparing them. `=` and `!=` compare the operand tokens directly.

Variable dereferencing inside `if` conditions is not currently implemented.

### Blocks

Braces delimit the body executed by a successful `if` condition:

```meitner
if 1 = 1 {
    print "inside block"
}
```

Nested brace blocks are not currently supported by the tokenizer.

## Current language limitations

The present implementation is intentionally minimal. In particular:

- there are no user-defined functions
- there are no loops
- there is no `else`
- there are no arrays or collections despite square brackets being used for variable references
- there are no Boolean literals
- there is no general expression grammar
- arithmetic is currently limited to `addvar`
- string escape sequences are not implemented
- variable references are only implemented in specific statement positions
- nested brace blocks are not implemented
- variables are stored in one shared environment, including code executed inside a conditional block

## Documentation

See [Language Reference](docs/LANGUAGE.md) for a complete reference to the currently implemented Meitner syntax and behavior.

## License

Meitner is licensed under the terms contained in [LICENSE](LICENSE).