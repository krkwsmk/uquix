# UQUIX Headers Rules Configuration Guide

*This guide helps you to configure your own headers rules. UQUIX by default uses `uquix/configs/headers_rules.json` rules to generate headers.

*You can see how the headers will be generated from `uquix/configs/headers_rules.json` by executing `uquix/src/uquix/headers_generator.py`.

*Execute `uquix/src/uquix/headers_generator.py` multiple times to see how the headers will be generated based on `uquix/configs/headers_rules.json`.

*UQUIX by default will generate headers based on `uquix/configs/headers_rules.json`, but you can set your own headers rules file by `--headers-rules-file` option.

----------

## Table of Contents

1. [Rules Overview](#rules-overview)
2. [Rules Definitions](#rules-definitions)
   - [Core Rules](#core-rules)
   - [Multi-Type-Rule Rules](#multi-type-rule-rules)
3. [Special Syntax](#special-syntax)
4. [403 Bypass Headers](#403-bypass-headers)
5. [WARNING](#warning)

----------

## Rules Overview

| Rule            | Applies To    | Values              | Default     | Required                  |
|-----------------|---------------|---------------------|-------------|---------------------------|
| `type`          | All           | `simple`/`multi`    | -           | Yes                       |
| `items`         | All           | List of strings     | -           | Yes                       |
| `isalways`      | All           | `true`/`false`      | `false`     | No                        |
| `israndomplace` | All           | `true`/`false`      | `true`      | No                        |
| `repeat`        | All           | Integer/syntax      | `0`         | No                        |
| `is403`         | All           | `true`/`false`      | `false`     | No                        |
| `sep`           | `multi` only  | String              | `", "`      | No                        |
| `isunique`      | `multi` only  | `true`/`false`      | `true`      | No                        |
| `israndom_count`| `multi` only  | `true`/`false`      | `true`      | No                        |
| `count`         | `multi` only  | Integer/syntax      | -           | If `israndom_count: false`|

----------

## Rules Definitions

### Core Rules (Apply to All Headers)

#### 1. `type` *(Required)*
- **Purpose**: Determines how values are selected from the `items` rule list.
- **Values**:
  - `simple`: Select **single** random value from `items` rule per request.
  - `multi`: Select **multiple** random values from `items` rule per request (joined by a separator (`sep` rule)).
- **Behavior**:
  - Controls which additional rules are allowed (ex, `multi` type rule can use `sep` rule).
  - Finalizes header structure early in generation

#### 2. `items` *(Required)*
- **Purpose**: List of possible values for the header.
- **Syntax**:
  - Values: `["a", "b", "c", "anything", ...]`
  - Dynamic placeholders (explained in [Special Syntax](#special-syntax)):
    - `{NUM->min_max}`: Random number generator.
    - `{[a,b,c,...]}`: Random selection from a list.
    *Every element can contain a dynamic placeholders*

#### 3. `isalways`
- **Purpose**: Control header inclusion in requests.
- **Type**: Boolean (`true`/`false`).
- **Default**: `false`
- **Behavior**:
  - `true`: Header is included in **every** request.
  - `false`: Header is randomly included/excluded per request.

#### 4. `israndomplace`
- **Purpose**: Control header order randomization.
- **Type**: Boolean (`true`/`false`).
- **Default**: `true`
- **Behavior**:
  - `true`: Header position changes randomly per request (unless all headers have `israndomplace: false`).
  - `false`: Header retains fixed position.

#### 5. `repeat`
- **Purpose**: Final value duplication control.
- **Type**: Integer or dynamic syntax.
- **Default**: `0` (no repetition).
- **Syntax**:
  - Integer: (ex, `3`)
  - Range: `{NUM->min_max}` (ex, `{NUM->5_10}`: the final value will be repeated as the random picked number from the range 5->10).
  - List: `{[1,3,5]}` (randomly pick 1, 3, or 5 repetitions).
  - `MAX`: Use maximum allowed value (repeat the final value as the number of all items in `items` rule).
  *`MAX` can be used in the `Integer` or `Range` or `List`.

#### 6. `is403`
- **Purpose**: Mark headers used for bypassing 403 Forbidden.
- **Type**: Boolean (`true`/`false`).
- **Default**: `false`
- **Behavior**:
  - Headers with `is403: true` are excluded when running uquix with `--no-403headers`.

----------

### Multi-Type-Rule Rules

*This Rules only works when `type` rule is `multi`.

#### 1. `sep`
- **Purpose**: Define separator between multiple values.
- **Type**: String.
- **Default**: `", "`
- **Example**: `sep: "|"` → `gzip|deflate`.

#### 2. `isunique`
- **Purpose**: Control in allowing duplicated values.
- **Type**: Boolean (`true`/`false`).
- **Default**: `true`
- **Behavior**:
  - `true`: All selected values must be unique.
  - `false`: Allow duplicates (ex, `en, en`).

#### 3. `israndom_count`
- **Purpose**: Randomize the number of picked values from `items` rule.
- **Type**: Boolean (`true`/`false`).
- **Default**: `true`
- **Behavior**:
  - `true`: Randomly pick values from 1 to total items count.
  - `false`: Use the `count` rule to determine the exact number of needed picked values.

#### 4. `count`
- **Purpose**: Set the number of values to pick from `items` rule (when `israndom_count: false`).
- **Type**: Integer or dynamic syntax.
- **Syntax**:
  - Same as `repeat` rule ( `INT`, `{NUM->min_max}`, `{[list]}`, `MAX`).
- **Example**: `count: "{NUM->2_5}"` → Pick random number of values from 2 to 5.

----------

## Special Syntax

### 1. `{NUM->min_max}`
- **Purpose**: Generate a random integer within a range.
- **Syntax**: `{NUM->start_end}`
- **Example**:
  - `{NUM->1_255}` → Random number between 1->255.
  - `{NUM->1000_9999}` → radom 4-digit number between 1000->9999.

### 2. `{[item1,item2,...]}`
- **Purpose**: Randomly select an item from the list.
- **Syntax**: `{[value1,value2,value3]}`
- **Example**:
  - `{[no-cache,max-age=0]}` → Randomly picks `no-cache` or `max-age=0`.
    
### 3. **Mixed Special-Syntax Example:
        "Warning": {
            "type": "simple",
            "items": ["{[110,199,214]} {[Stale,Expired]} yeah this is static", "{NUM->110_300} {[Miscellaneous warning,Response is stale]} staticccc"]
        }


----------

## 403 Bypass Headers

Headers marked with `is403: true` are designed to bypass 403 Forbidden. Examples include:

- Spoofed IP addresses (`X-Forwarded-For`, `X-Real-IP`).
- Admin path probes (`Referer: /admin`).
- Uncommon headers like `X-Original-URL`.

**Handling**:

- Use `--no-403headers` to exclude all headers with `is403: true`.

----------

## NOTES:
    
    1. **Check `--random-headers` option in the uquix help section. Its an important option.**
    
    2. **If `--random-headers` is `0`, so only headers that has `isalways` rule is `true` will be sent.**
    
    3. **Use `--random-agents` to randomize the User-Agent per request. Default User-Agent is `UQUIX/1.0.0`.**

----------

#### WARNING:

*PLEASE customize your rules `CAREFULLY` and do NOT test any web server BEFORE ASKING FOR `PERMISSIONS`.


################################################################
# By: Abd Almoen Arafa (0.1Arafa)                              #
# Age: 18                                                      #
# Year: 2025                                                   #
#######################################################################
# WARNING: Please ask for PERMISSIONS before testing any web server.  #
# Use this tool AT YOUR OWN RISK.                                     #
# I'm NOT responsible for any unethical action.                       #
#######################################################################
