# Meitner Language Reference

This document describes the Meitner language as implemented by the current interpreter.

## 1. Source structure

A program is a sequence of whitespace-separated tokens. Spaces and line breaks are equivalent outside quoted strings, so conventional line-based formatting is recommended but not required.

Comments start with `//` and run to the end of the line:

```meitner
// this is a comment
print "hello"   // so is this
```

Because words are split on whitespace, operators and brackets must be written as separate tokens: `[ x ]`, `a = b`, `1 > 2`.

## 2. Special characters

| Character | Meaning |
| --- | --- |
| `"` | Delimits a string. There is no escape syntax, so a string cannot contain `"`. |
| `[` `]` | Wrap a variable name: `[ name ]`. They are not arrays. |
| `{` `}` | Delimit a block. Blocks can be nested. |

## 3. Values

A value is one of:

| Form | Type | Example |
| --- | --- | --- |
| bare number | integer | `10` |
| quoted text | string | `"hello"` |
| `true` / `false` | boolean | `true` |
| `[ name ]` | whatever the variable holds | `[ score ]` |
| any other bare word | plain word (a string) | `hello` |

A quoted `"true"` is a string, not a boolean. A quoted `"5"` is a string, not the integer `5`, though arithmetic can still convert it.

Booleans print as `true` / `false`.

## 4. Variables

```meitner
setvar [ name ] value
```

Creates the variable, or replaces its value if it exists. The value can be any value form, including another variable:

```meitner
setvar [ a ] 5
setvar [ b ] [ a ]
```

All variables live in one shared global environment, including variables set inside blocks. Blocks have no local scope. Referencing an undefined variable is an error.

## 5. Printing

```meitner
print value
```

Prints any value form: `print "hi"`, `print 42`, `print true`, `print [ x ]`.

## 6. Arithmetic

```meitner
addvar  [ x ] value     // x = x + value
subvar  [ x ] value     // x = x - value
multvar [ x ] value     // x = x * value
divvar  [ x ] value     // x = x // value
```

- The variable must already exist.
- The operand can be a number or a `[ variable ]`.
- Both sides are converted to integers. Booleans and non-numeric text raise an error.
- `divvar` is **integer (floor) division**: `10` divided by `4` gives `2`, and `-7` divided by `2` gives `-4`. This keeps variables whole numbers.
- Dividing by zero is an error.

## 7. Conditionals

### Boolean form

```meitner
if true { ... }
if [ flag ] { ... }
```

The condition must be a boolean (a literal or a variable holding one). Anything else is an error.

### Comparison form

```meitner
if left op right { ... }
```

`left` and `right` can be any value, including `[ variables ]`.

| Operator | Meaning |
| --- | --- |
| `=` | equal: same type **and** same value |
| `!=` | not equal |
| `>` | greater than (both sides converted to integers) |
| `<` | less than (both sides converted to integers) |

Because `=` checks the type, `true = 1` is false and `5 = "5"` is false.

### else

```meitner
if 3 > 5 {
    print "bigger"
}
else {
    print "not bigger"
}
```

`else` must directly follow an `if` block. There is no `else if` keyword, but since blocks nest you can write:

```meitner
if x = 1 {
    print "one"
}
else {
    if x = 2 {
        print "two"
    }
}
```

## 8. Loops

```meitner
loop 3 {
    print "hi"
}
```

Repeats the block a fixed number of times. The count can be a number or a `[ variable ]`. A count of zero or less runs the block zero times.

```meitner
loop forever {
    print "tick"
}
```

Runs until the program is interrupted with Ctrl+C. There is no `break` yet.

## 9. Blocks

A block is `{ ... }` containing statements. Blocks are used as bodies of `if`, `else` and `loop`, and can be nested to any depth. They share the global variable environment.

## 10. Errors

Errors stop the program and print a message to standard error. The process exits with status 1. Common errors: undefined variable, unknown command, unterminated string or block, non-numeric value in arithmetic, division by zero.

## 11. Not yet implemented

- functions, arguments and return values
- `break`
- arrays, lists, maps and other collections
- general expressions and operator precedence (`x + 5`, `(2 + 3) * 4`)
- modulus and exponentiation
- string interpolation and string escapes
- local block scope
- imports and modules

## 12. Grammar

An approximate description; the interpreter works directly on token positions rather than building a syntax tree.

```text
program    := statement*

statement  := "print" value
            | "setvar" name value
            | ("addvar" | "subvar" | "multvar" | "divvar") name value
            | "if" condition block ("else" block)?
            | "loop" (value | "forever") block

condition  := value                      // must be a boolean
            | value comparison value

comparison := "=" | "!=" | ">" | "<"

block      := "{" statement* "}"
name       := "[" word "]"
value      := string | boolean | name | number | word
boolean    := "true" | "false"
string     := '"' characters '"'
```
