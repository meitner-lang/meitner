# Meitner Language Reference

This document describes the Meitner language as implemented by the current interpreter.

Meitner is still an early language. This reference therefore distinguishes current behavior from syntax that might be expected in a more complete programming language but is not yet implemented.

## 1. Source structure

A Meitner program consists of whitespace-separated tokens and quoted strings.

For example:

```meitner
print "hello"
```

Whitespace separates ordinary tokens. Spaces and line breaks are generally equivalent outside quoted strings.

This means these programs have the same token structure:

```meitner
setvar [ x ] 5
print [ x ]
```

```meitner
setvar
[
x
]
5

print
[
x
]
```

Using conventional line-based formatting is strongly recommended for readability.

## 2. Tokens

The tokenizer recognizes several special characters.

### Double quotes

Double quotes delimit strings:

```meitner
"hello world"
```

Whitespace inside a quoted string is preserved as part of the string.

Strings cannot currently contain an escaped double quote. There is no implemented escape syntax such as `\"`.

### Square brackets

Square brackets are individual tokens:

```meitner
[ variable ]
```

They are currently used to mark variable references in statements that support variable lookup.

They do not represent arrays or lists.

### Curly braces

Curly braces delimit a block:

```meitner
{
    print "hello"
}
```

Blocks are currently used with `if` and `else`.

Nested curly-brace blocks are not supported by the current tokenizer.

## 3. Values

Meitner does not currently have a general runtime type system.

Values are primarily stored as textual values, integer values produced by arithmetic statements, or boolean values.

### String values

Quoted values represent strings:

```meitner
"hello"
"Meitner language"
```

When used with `setvar`, the surrounding quotes are not stored as part of the variable value.

```meitner
setvar [ message ] "hello"
```

The value of `message` is:

```text
hello
```

### Boolean values

`true` and `false` are boolean literals. They are written without quotes:

```meitner
setvar [ ready ] true
setvar [ done ] false
```

When used with `setvar`, these are stored as real boolean values, not as text.

A quoted `"true"` or `"false"` is an ordinary string and is not treated as a boolean:

```meitner
setvar [ a ] true
setvar [ b ] "true"
```

Here `a` is a boolean and `b` is a string.

Booleans print in lowercase as `true` or `false`.

Booleans cannot be used in arithmetic. See section 6.

### Unquoted values

An unquoted value (other than `true` or `false`) is stored as its token text when passed to `setvar`.

```meitner
setvar [ amount ] 10
```

Initially, `amount` is stored as the token representing `10`.

Numeric operations can later convert such values to integers.

## 4. Variables

Variables form a mutable global environment.

### Assignment

Syntax:

```meitner
setvar [ name ] value
```

Example:

```meitner
setvar [ language ] "Meitner"
```

Another example:

```meitner
setvar [ count ] 5
```

A boolean example:

```meitner
setvar [ flag ] true
```

If the variable does not exist, `setvar` creates it.

If the variable already exists, `setvar` replaces its value.

```meitner
setvar [ count ] 5
setvar [ count ] 20
```

After these statements, `count` contains `20`.

### Variable names

Variable names are represented by the token between `[` and `]`:

```meitner
setvar [ score ] 10
```

Here, the variable name is `score`.

There is currently no separate validation rule restricting identifiers to letters, digits, or underscores. The interpreter treats the token in the expected variable-name position as the name.

For clarity and future compatibility, simple identifier-style names are recommended:

```meitner
score
player_name
counter1
```

## 5. Printing

The `print` statement sends a value to output.

### Printing a quoted string

Syntax:

```meitner
print "text"
```

Example:

```meitner
print "Hello, world!"
```

### Printing a boolean literal

Syntax:

```meitner
print true
print false
```

These output `true` and `false` respectively.

### Printing a variable

Syntax:

```meitner
print [ variable ]
```

Example:

```meitner
setvar [ greeting ] "hello"
print [ greeting ]
```

The interpreter looks up the variable by name and prints its stored value. Boolean variables print as `true` or `false`.

```meitner
setvar [ ready ] true
print [ ready ]
```

### Printing other unquoted literals

The current interpreter's `print` implementation is structured around quoted strings, boolean literals, and bracketed variable references.

Code should therefore use one of these documented forms:

```meitner
print "hello"
```

```meitner
print true
```

or:

```meitner
print [ name ]
```

## 6. Arithmetic

Meitner implements four arithmetic statements. Each one modifies an existing variable in place: `addvar`, `subvar`, `multvar`, and `divvar`.

### `addvar`

Syntax:

```meitner
addvar [ variable ] amount
```

Example:

```meitner
setvar [ score ] 10
addvar [ score ] 5
print [ score ]
```

The operation behaves conceptually as:

```text
variable = int(variable) + int(amount)
```

### `subvar`

Syntax:

```meitner
subvar [ variable ] amount
```

Conceptually:

```text
variable = int(variable) - int(amount)
```

Example:

```meitner
setvar [ lives ] 3
subvar [ lives ] 1
print [ lives ]
```

### `multvar`

Syntax:

```meitner
multvar [ variable ] amount
```

Conceptually:

```text
variable = int(variable) * int(amount)
```

Example:

```meitner
setvar [ total ] 6
multvar [ total ] 7
print [ total ]
```

### `divvar`

Syntax:

```meitner
divvar [ variable ] amount
```

Conceptually:

```text
variable = int(variable) / int(amount)
```

`divvar` uses true division, so the result may be a decimal number rather than an integer. For example, dividing `10` by `4` produces `2.5`.

Dividing by zero is an error.

### Arithmetic requirements

For all four statements, both the existing variable value and the supplied operand must be convertible to integers.

Booleans cannot be used in arithmetic. If the variable holds a boolean, or the operand is `true` or `false`, the interpreter raises an error instead of treating the boolean as 0 or 1.

### Arithmetic limitations

There are currently no statements for:

- modulus
- exponentiation

Meitner also does not yet have general arithmetic expressions such as:

```text
x + 5
```

or:

```text
(2 + 3) * 4
```

## 7. Conditions

Meitner supports conditional execution with `if`, and an optional `else`.

There are two forms of condition.

### Comparison form

```meitner
if left operator right {
    statements
}
```

Example:

```meitner
if 10 > 4 {
    print "greater"
}
```

When the comparison succeeds, the block is executed.

When it fails, the block is skipped.

### Boolean form

```meitner
if true {
    statements
}
```

```meitner
if false {
    statements
}
```

With a single boolean literal as the condition, the block runs for `true` and is skipped for `false`.

The condition must be the literal `true` or `false`. A variable reference such as `if [ flag ] { ... }` is not supported. See section 9.

### `else`

An `if` block may be followed by an `else` block:

```meitner
if left operator right {
    statements
}
else {
    statements
}
```

The `else` block runs when the condition is false. Exactly one of the two blocks runs.

Example:

```meitner
if 3 > 5 {
    print "bigger"
}
else {
    print "not bigger"
}
```

This prints `not bigger`.

`else` works with both condition forms:

```meitner
if false {
    print "never runs"
}
else {
    print "else runs"
}
```

Because whitespace is ignored, `} else {` on a single line is equivalent to placing `else` on its own line.

An `else` must directly follow the block of an `if`. A standalone `else` is not a valid statement.

There is no `else if`. Since nested blocks are not supported, an `if` cannot currently appear inside an `else` block either.

## 8. Comparison operators

Four comparison operators are implemented for the comparison form.

### Equality: `=`

```meitner
if hello = hello {
    print "equal"
}
```

Equality compares the two operand tokens directly.

### Inequality: `!=`

```meitner
if hello != world {
    print "different"
}
```

Inequality compares the operand tokens directly.

### Greater than: `>`

```meitner
if 10 > 5 {
    print "greater"
}
```

Both operands are converted to integers before comparison.

### Less than: `<`

```meitner
if 3 < 7 {
    print "less"
}
```

Both operands are converted to integers before comparison.

### Comparing booleans

Because `=` and `!=` compare tokens directly, `true` and `false` can be used as operands:

```meitner
if true = true {
    print "equal"
}

if true != false {
    print "different"
}
```

`>` and `<` cannot be used with booleans, since they require integer operands.

## 9. Conditions and variables

Variable lookup is not currently implemented for condition operands.

For example, although bracket syntax can retrieve a variable for `print`:

```meitner
print [ score ]
```

the current `if` implementation does not evaluate:

```text
[ score ]
```

as a variable expression.

This also means a boolean variable cannot yet be used directly as a condition. Boolean variables can currently be stored and printed, but not tested.

Conditions should therefore currently use literal operands:

```meitner
if 10 > 5 {
    print "true"
}
```

rather than relying on variable substitution in the condition.

## 10. Blocks

A block is delimited by `{` and `}`.

```meitner
{
    print "inside"
}
```

Blocks currently serve as the bodies of `if` and `else` statements:

```meitner
if 1 = 1 {
    print "condition succeeded"
}
else {
    print "condition failed"
}
```

The block is tokenized as a separate group and passed back to the interpreter when it is selected to run.

### Shared variables

Conditional blocks use the same variable environment as surrounding code, including `else` blocks.

For example:

```meitner
setvar [ value ] 1

if 1 = 1 {
    setvar [ value ] 2
}

print [ value ]
```

After the block executes, `value` is `2`.

Blocks do not currently introduce their own variable scope.

### Nested blocks

Nested brace blocks are not supported by the current tokenizer.

Code such as:

```text
if 1 = 1 {
    if 2 = 2 {
        print "nested"
    }
}
```

should not currently be considered valid supported Meitner syntax.

## 11. Statement summary

### `print`

Quoted string:

```meitner
print "text"
```

Boolean literal:

```meitner
print true
```

Variable:

```meitner
print [ variable ]
```

### `setvar`

Unquoted value:

```meitner
setvar [ variable ] value
```

Quoted value:

```meitner
setvar [ variable ] "value"
```

Boolean value:

```meitner
setvar [ variable ] true
```

### Arithmetic

```meitner
addvar [ variable ] integer
subvar [ variable ] integer
multvar [ variable ] integer
divvar [ variable ] integer
```

### `if`

```meitner
if left = right {
    statements
}
```

```meitner
if left != right {
    statements
}
```

```meitner
if integer > integer {
    statements
}
```

```meitner
if integer < integer {
    statements
}
```

```meitner
if true {
    statements
}
```

### `if` with `else`

```meitner
if condition {
    statements
}
else {
    statements
}
```

## 12. Complete examples

### Variables

```meitner
setvar [ name ] "Meitner"
print [ name ]
```

### Mutation

```meitner
setvar [ message ] "first"
print [ message ]

setvar [ message ] "second"
print [ message ]
```

### Integer arithmetic

```meitner
setvar [ points ] 25
addvar [ points ] 10
print [ points ]

subvar [ points ] 5
print [ points ]

multvar [ points ] 2
print [ points ]
```

### Booleans

```meitner
setvar [ ready ] true
print [ ready ]

setvar [ ready ] false
print [ ready ]
```

### Conditional equality

```meitner
if alpha = alpha {
    print "equal"
}
```

### Conditional inequality

```meitner
if alpha != beta {
    print "different"
}
```

### Numeric comparison

```meitner
if 100 > 25 {
    print "100 is greater"
}

if 4 < 8 {
    print "4 is less"
}
```

### Boolean conditions

```meitner
if true {
    print "always runs"
}

if false {
    print "never runs"
}
```

### If and else

```meitner
if 3 > 5 {
    print "bigger"
}
else {
    print "not bigger"
}
```

### Boolean condition with else

```meitner
if false {
    print "never runs"
}
else {
    print "else runs"
}
```

### Modifying state inside a condition

```meitner
setvar [ result ] "before"

if yes = yes {
    setvar [ result ] "after"
}

print [ result ]
```

### Modifying state inside an else block

```meitner
setvar [ result ] "before"

if 1 = 2 {
    setvar [ result ] "if branch"
}
else {
    setvar [ result ] "else branch"
}

print [ result ]
```
