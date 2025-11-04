# Python Garbage Collector Explorer

A diagnostic and educational tool for exploring Python's garbage collection behavior, including cycle detection, object tracking, and memory management.

## Features

- Demonstrate reference counting and cycle detection
- Visualize garbage collection statistics
- Test weak references
- Monitor object lifecycle and finalization
- Interactive GC control and inspection

## Requirements

No external dependencies - uses Python standard library only.

## Usage

```bash
# Run GC demonstrations
python3 py-GC.py

# Run with color output
python3 py-GC.py --color

# View GC statistics
python3 py-GC.py --stats
```

## What it demonstrates

- Reference cycles and how GC handles them
- Weak references vs strong references
- Object finalization with `__del__`
- GC generation tracking
- Memory management best practices

## Platform

Cross-platform (Python 3.6+)
