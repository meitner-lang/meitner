# Meitner

Meitner is a small interpreted programming language with a compact, whitespace-oriented syntax.

The current language includes:

- quoted string literals
- integer-like literal values
- boolean literals (`true` and `false`)
- mutable variables
- bracketed variable references
- printing
- integer arithmetic on existing variables (`addvar`, `subvar`, `multvar`, `divvar`)
- conditional execution with optional `else`
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
else {
    print "something went wrong"
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

### Booleans

`true` and `false` are boolean literals. They are written without quotes:

```meitner
setvar [ ready ] true
print [ ready ]
```

Booleans print in lowercase (`true` / `false`). A quoted `"true"` is an ordinary string, not a boolean.

Booleans cannot be used in arithmetic. Passing one to `addvar`, `subvar`, `multvar`, or `divvar` raises an error.

### Variables

Create or replace a variable with `setvar`:

```meitner
setvar [ name ] "Meitner"
setvar [ count ] 10
setvar [ flag ] false
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

Print a boolean literal:

```meitner
print true
```

Print a variable:

```meitner
print [ name ]
```

### Arithmetic

Arithmetic statements convert the variable's current value and the supplied value to integers, apply the operation, and store the result back in the variable:

| Statement | Operation |
| --- | --- |
| `addvar [ x ] n` | `x = x + n` |
| `subvar [ x ] n` | `x = x - n` |
| `multvar [ x ] n` | `x = x * n` |
| `divvar [ x ] n` | `x = x / n` |

```meitner
setvar [ count ] 10
addvar [ count ] 5
print [ count ]
```

After the addition, `count` contains the integer value `15`.

Note that `divvar` uses true division, so its result may be a decimal number (for example, `10 / 4` gives `2.5`).

### Conditionals

Conditional blocks use `if`, a condition, and a brace-delimited block. There are two condition forms.

**Comparison** (two literal operands and an operator):

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

**Boolean literal** (a single `true` or `false`):

```meitner
if true {
    print "always runs"
}
```

Variable dereferencing inside `if` conditions is not currently implemented, so `if [ flag ] { ... }` does not work yet.

### Else

An `if` block can be followed by an `else` block. The `else` block runs when the condition is false:

```meitner
if 3 > 5 {
    print "bigger"
}
else {
    print "not bigger"
}
```

This prints `not bigger`. `else` works with both condition forms:

```meitner
if false {
    print "never runs"
}
else {
    print "else runs"
}
```

There is no `else if`, since nested blocks are not supported.

### Blocks

Braces delimit the body executed by a successful `if` condition (or by `else` when the condition fails):

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
- there is no `else if`
- there are no arrays or collections despite square brackets being used for variable references
- there is no general expression grammar
- arithmetic is limited to the four variable statements above, and booleans cannot be used in it
- string escape sequences are not implemented
- variable references are only implemented in specific statement positions (not in `if` conditions)
- nested brace blocks are not implemented
- variables are stored in one shared environment, including code executed inside a conditional block

## Documentation

See [Language Reference](docs/LANGUAGE.md) for a complete reference to the currently implemented Meitner syntax and behavior.

## License

Meitner is licensed under the terms contained in [LICENSE](LICENSE).