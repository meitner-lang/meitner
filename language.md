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

Blocks are currently used with `if`.

Nested curly-brace blocks are not supported by the current tokenizer.

## 3. Values

Meitner does not currently have a general runtime type system.

Values are primarily stored as either textual values or integer values produced by `addvar`.

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

### Unquoted values

An unquoted value is stored as its token text when passed to `setvar`.

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

The interpreter looks up the variable by name and prints its stored value.

### Printing unquoted literals

The current interpreter's `print` implementation is structured specifically around quoted values or bracketed variable references.

Code should therefore use one of these documented forms:

```meitner
print "hello"
```

or:

```meitner
print [ name ]
```

## 6. Arithmetic

Meitner currently implements one arithmetic statement: `addvar`.

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

Both the existing variable value and the supplied operand must therefore be convertible to integers.

For example:

```meitner
setvar [ count ] 8
addvar [ count ] 2
```

produces an integer value of `10`.

### Arithmetic limitations

There are currently no corresponding statements for:

- subtraction
- multiplication
- division
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

Meitner supports conditional execution with `if`.

General syntax:

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

There is currently no `else` statement.

## 8. Comparison operators

Four comparison operators are implemented.

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

Blocks currently serve as the bodies of `if` statements:

```meitner
if 1 = 1 {
    print "condition succeeded"
}
```

The block is tokenized as a separate group and passed back to the interpreter when its condition succeeds.

### Shared variables

Conditional blocks use the same variable environment as surrounding code.

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

### `addvar`

```meitner
addvar [ variable ] integer
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

### Integer addition

```meitner
setvar [ points ] 25
addvar [ points ] 10
print [ points ]
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

### Modifying state inside a condition

```meitner
setvar [ result ] "before"

if yes = yes {
    setvar [ result ] "after"
}

print [ result ]
```

## 13. Features not currently implemented

The current Meitner interpreter does not implement:

- functions
- function arguments
- return values
- loops
- `else`
- Boolean literals
- arrays
- lists
- maps or dictionaries
- objects or structures
- imports or modules
- user-defined types
- general expressions
- operator precedence
- subtraction
- multiplication
- division
- string interpolation
- string escapes
- nested brace blocks
- local block scope
- variable evaluation inside conditions
- comments

These should not be treated as part of the current language unless the interpreter is extended to support them.

## 14. Current grammar

The implemented language can be approximately described as:

```text
program       := statement*

statement     := print_statement
               | setvar_statement
               | addvar_statement
               | if_statement

print_statement
              := "print" string
               | "print" "[" identifier "]"

setvar_statement
              := "setvar" "[" identifier "]" value

addvar_statement
              := "addvar" "[" identifier "]" integer

if_statement  := "if" operand comparison operand block

comparison    := "="
               | "!="
               | ">"
               | "<"

block         := "{" statement* "}"

value         := string
               | token

operand       := token

string        := "\"" characters "\""
```

This grammar is descriptive rather than a formal parser specification. The current interpreter operates directly on token positions rather than parsing a complete abstract syntax tree.