# Python Garbage Collector Explorer

A diagnostic and educational tool for exploring Python's garbage collection behavior, including cycle detection, object tracking, and memory management.

## Features

- Demonstrate reference counting and cycle detection
- Visualize garbage collection statistics
- Test weak references with proper lifecycle demonstration
- Monitor object lifecycle and finalization
- Interactive GC control and inspection
- Detailed error handling and user feedback

## Requirements

No external dependencies - uses Python standard library only.

**Python 3.6+** (some features require Python 3.4+)

## Usage

### Basic Usage

```bash
# Run basic GC demonstration (creates 1 cycle by default)
python3 py-GC.py

# Create multiple circular reference pairs
python3 py-GC.py --cycles 5

# View detailed GC statistics
python3 py-GC.py --stats
```

### Advanced Options

```bash
# Demonstrate weak references and their lifecycle
python3 py-GC.py --weakref-demo

# Break cycles manually before garbage collection
python3 py-GC.py --cycles 3 --break-cycles

# Keep uncollectable objects for inspection
python3 py-GC.py --saveall

# Suppress GC debug output (reduces noise)
python3 py-GC.py --no-debug

# Combine multiple options
python3 py-GC.py --cycles 10 --weakref-demo --saveall
```

### Color Output Options

Control colored output with the `--color` option:

```bash
# Auto-detect terminal support (default)
python3 py-GC.py --color auto

# Always show colors
python3 py-GC.py --color always

# Never show colors
python3 py-GC.py --color never
```

You can also disable colors using the `NO_COLOR` environment variable (respects the [NO_COLOR standard](https://no-color.org/)):

```bash
NO_COLOR=1 python3 py-GC.py
```

### Command-Line Options

```
--cycles CYCLES        Number of circular reference pairs to create (must be >= 1)
--stats               Display detailed GC statistics and configuration
--weakref-demo        Demonstrate weak references and their lifecycle
--break-cycles        Break circular references before collection (manual cleanup)
--saveall             Keep uncollectable objects for inspection
--no-debug            Suppress GC debug output (reduces noise from internal objects)
--color {auto,always,never}
                      Colorize output: auto (default), always, or never
```

## What It Demonstrates

### 1. Reference Cycles and Garbage Collection

Python uses reference counting for memory management, but circular references create a problem:

```python
# Two objects reference each other
a.other = b
b.other = a
```

When no external references exist, Python's garbage collector detects and cleans up these cycles.

### 2. Weak References

Weak references allow you to reference an object without preventing its garbage collection:

```bash
python3 py-GC.py --weakref-demo
```

The demo shows:
- Objects alive with strong references (weakrefs return the object)
- Objects die when strong references are deleted (weakrefs return None)

### 3. Object Finalization

The `__del__` method demonstrates object finalization. The tool safely handles edge cases where `__del__` might fail during interpreter shutdown.

### 4. GC Generation Tracking

Python's GC uses generational collection (gen 0, 1, 2). Use `--stats` to see:
- Objects per generation
- Collection statistics
- GC thresholds and configuration

### 5. Manual Cycle Breaking

Use `--break-cycles` to see the difference between manual cleanup and automatic garbage collection:

```bash
# With manual cleanup (no GC needed)
python3 py-GC.py --cycles 5 --break-cycles

# Without manual cleanup (GC collects cycles)
python3 py-GC.py --cycles 5
```

## Examples

### Example 1: Basic Cycle Detection

```bash
$ python3 py-GC.py --cycles 2
Creating 2 cycle(s)...
Dropping local references to cycles...

Collecting garbage...
GC collected 4 unreachable objects.
Deleting A0
Deleting B0
Deleting A1
Deleting B1
```

### Example 2: GC Statistics

```bash
$ python3 py-GC.py --stats
=== Python Garbage Collector Statistics ===

GC Configuration:
  Enabled: True
  Debug flags: 0
  Thresholds: gen0=700, gen1=10, gen2=10
  Object count: 8234

GC Statistics by Generation:
  Generation 0:
    Collections: 45
    Collected: 1250
    Uncollectable: 0
  ...
```

### Example 3: Weak References

```bash
$ python3 py-GC.py --weakref-demo

=== Weakref Demonstration ===
Creating objects with weak references...
Objects referenced by weakrefs? A=True B=True
Objects are alive because we hold strong references to them.

Deleting strong references...
Deleting Weak-A
Deleting Weak-B
Objects referenced by weakrefs? A=False B=False
Weakrefs now point to None because objects were garbage collected.
```

## Educational Value

This tool is designed to help developers understand:

1. **Why circular references matter** - They can't be cleaned up by reference counting alone
2. **When to use weak references** - Caches, observers, callbacks that shouldn't prevent cleanup
3. **How Python's GC works** - Generational collection, thresholds, and cycle detection
4. **Memory management best practices** - Breaking cycles manually vs automatic collection

## Platform

Cross-platform - runs on Linux, macOS, and Windows

**Tested on:** Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12+

## Error Handling

The tool includes comprehensive error handling:
- Safe `__del__` implementation that won't crash during shutdown
- Graceful handling of repr() failures on objects
- Validation of command-line arguments
- Detection of conflicting options
- Truncation of overly long object representations

## Contributing

This is an educational tool. Suggestions for improvements and additional demonstrations are welcome!

## License

MIT License - feel free to use for learning and teaching Python memory management.
