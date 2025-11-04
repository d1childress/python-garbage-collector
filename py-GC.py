#!/usr/bin/env python3
import argparse
import gc
import os
import sys
from dataclasses import dataclass
from typing import Optional, List, Tuple
import weakref
from weakref import ReferenceType
from contextlib import contextmanager


COLOR_ENABLED = False
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def color(text: str, *codes: str) -> str:
    if not COLOR_ENABLED or not codes:
        return text
    return f"{''.join(codes)}{text}{RESET}"


@dataclass
class Node:
    name: str
    other: Optional["Node"] = None

    def __del__(self):
        # Demonstrate finalization; this can interact with GC for cycles
        # Wrap in try/except to prevent crashes during interpreter shutdown
        # when global variables (color, YELLOW, sys.stdout) may be unavailable
        try:
            print(color(f"Deleting {self.name}", YELLOW))
        except Exception:
            # Silently ignore errors in __del__ to prevent crashes
            pass


def make_cycle_pair(a_name: str, b_name: str) -> List[Node]:
    a = Node(a_name)
    b = Node(b_name)
    a.other = b
    b.other = a
    return [a, b]


def break_cycle(nodes: List[Node]) -> None:
    for node in nodes:
        node.other = None


def weakref_demo() -> Tuple[ReferenceType, ReferenceType, List[Node]]:
    """
    Demonstrate weak references properly by keeping objects alive.
    Returns weak references AND the objects themselves so they don't get GC'd immediately.
    """
    a = Node("Weak-A")
    b = Node("Weak-B")
    a_ref = weakref.ref(a)
    b_ref = weakref.ref(b)
    # Keep circular references, don't set to None yet
    a.other = b
    b.other = a
    # Return both weakrefs and the strong references to keep objects alive
    return a_ref, b_ref, [a, b]


@contextmanager
def temporary_gc_debug(flags: int):
    prev = gc.get_debug()
    gc.set_debug(flags)
    try:
        yield
    finally:
        gc.set_debug(prev)


def main() -> None:
    parser = argparse.ArgumentParser(description="Python GC cycle demonstration")
    parser.add_argument("--cycles", type=int, default=1,
                        help="Number of circular reference pairs to create (must be >= 1)")
    parser.add_argument("--saveall", action="store_true",
                        help="Keep uncollectable objects for inspection (shows objects in reference cycles)")
    parser.add_argument("--no-debug", action="store_true",
                        help="Suppress GC debug output (reduces noise from internal objects)")
    parser.add_argument("--break-cycles", action="store_true",
                        help="Break circular references before collection (demonstrates manual cleanup)")
    parser.add_argument("--weakref-demo", action="store_true",
                        help="Demonstrate weak references and their lifecycle")
    parser.add_argument("--stats", action="store_true",
                        help="Display detailed GC statistics and configuration")
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Colorize output: auto (default), always, or never",
    )
    args = parser.parse_args()

    global COLOR_ENABLED
    if args.color == "always":
        COLOR_ENABLED = True
    elif args.color == "never" or os.environ.get("NO_COLOR") is not None:
        COLOR_ENABLED = False
    else:
        COLOR_ENABLED = sys.stdout.isatty()

    # Handle --stats mode (standalone feature)
    if args.stats:
        print(color("=== Python Garbage Collector Statistics ===\n", BOLD, CYAN))

        print(color("GC Configuration:", BOLD))
        print(f"  Enabled: {gc.isenabled()}")
        print(f"  Debug flags: {gc.get_debug()}")
        thresholds = gc.get_threshold()
        print(f"  Thresholds: gen0={thresholds[0]}, gen1={thresholds[1]}, gen2={thresholds[2]}")
        print(f"  Object count: {len(gc.get_objects())}")

        print(color("\nGC Statistics by Generation:", BOLD))
        gen_stats = getattr(gc, "get_stats", None)
        if callable(gen_stats):
            try:
                stats = gc.get_stats()
                for gen, s in enumerate(stats):
                    print(color(f"  Generation {gen}:", GREEN))
                    print(f"    Collections: {s['collections']}")
                    print(f"    Collected: {s['collected']}")
                    print(f"    Uncollectable: {s['uncollectable']}")
            except Exception as e:
                print(color(f"  Error getting stats: {e}", RED))
        else:
            print(color("  get_stats() not available (Python < 3.4)", YELLOW))

        print(color("\nGC Counts (objects per generation):", BOLD))
        counts = gc.get_count()
        print(f"  Gen 0: {counts[0]} objects")
        print(f"  Gen 1: {counts[1]} objects")
        print(f"  Gen 2: {counts[2]} objects")

        print(color("\nReferrer count for common objects:", BOLD))
        sample_obj = object()
        print(f"  New object(): {len(gc.get_referrers(sample_obj))} referrers")

        return

    # Validate --cycles argument
    if args.cycles < 1:
        parser.error(f"--cycles must be >= 1 (got {args.cycles})")

    # Check for conflicting options
    if args.no_debug and args.saveall:
        parser.error("--saveall requires GC debug mode, cannot use with --no-debug")

    debug_flags = 0 if args.no_debug else gc.DEBUG_LEAK | (gc.DEBUG_SAVEALL if args.saveall else 0)

    print(color(f"Creating {args.cycles} cycle(s)...", BOLD, CYAN))
    holders: List[List[Node]] = []
    for i in range(args.cycles):
        pair = make_cycle_pair(f"A{i}", f"B{i}")
        holders.append(pair)

    if args.break_cycles:
        print(color(f"Breaking {len(holders)} cycle(s) before collection...", YELLOW))
        for pair in holders:
            break_cycle(pair)
        print(color("All cycles broken successfully.", GREEN))

    # Drop strong refs from our local list to simulate out-of-scope variables
    print(color("Dropping local references to cycles...", CYAN))
    holders = []

    if args.weakref_demo:
        print(color("\n=== Weakref Demonstration ===", BLUE, BOLD))
        print(color("Creating objects with weak references...", BLUE))
        aref, bref, weak_objects = weakref_demo()
        print(color(f"Objects referenced by weakrefs? A={aref() is not None} B={bref() is not None}", GREEN))
        print(color("Objects are alive because we hold strong references to them.", BLUE))

        # Now delete the strong references
        print(color("\nDeleting strong references...", YELLOW))
        del weak_objects
        gc.collect()  # Force collection
        print(color(f"Objects referenced by weakrefs? A={aref() is not None} B={bref() is not None}", RED))
        print(color("Weakrefs now point to None because objects were garbage collected.", BLUE))

    with temporary_gc_debug(debug_flags):
        # Add explanatory banner for debug output
        if not args.no_debug:
            print(color("\n--- GC Debug Output (showing collectable objects) ---", CYAN))
            print(color("Note: Objects below are detected and collected by GC", CYAN))

        print(color("\nCollecting garbage...", MAGENTA))
        try:
            collected = gc.collect()
            print(color(f"GC collected {collected} unreachable objects.", GREEN if collected else BLUE))
        except Exception as e:
            print(color(f"Error during garbage collection: {e}", RED))
            collected = 0

        if args.saveall and gc.garbage:
            print(color(f"\nUncollectable retained in gc.garbage: {len(gc.garbage)}", RED, BOLD))
            display_limit = 10
            for idx, obj in enumerate(gc.garbage[:display_limit], 1):
                try:
                    obj_repr = repr(obj)
                    # Truncate very long repr strings
                    if len(obj_repr) > 100:
                        obj_repr = obj_repr[:97] + "..."
                    print(color(f"  [{idx}] type={type(obj).__name__} repr={obj_repr}", RED))
                except Exception as e:
                    print(color(f"  [{idx}] type={type(obj).__name__} repr=<error: {e}>", RED))

            # Indicate if there are more objects not displayed
            if len(gc.garbage) > display_limit:
                print(color(f"  ... and {len(gc.garbage) - display_limit} more objects in gc.garbage", RED))

        gen_stats = getattr(gc, "get_stats", None)
        if callable(gen_stats):
            try:
                stats = gc.get_stats()
                print(color("\nGeneration stats:", BOLD))
                for gen, s in enumerate(stats):
                    print(
                        color(
                            f"  Gen {gen}: collections={s['collections']} collected={s['collected']} uncollectable={s['uncollectable']}",
                            CYAN,
                        )
                    )
            except Exception as e:
                print(color(f"\nError retrieving generation stats: {e}", RED))


if __name__ == "__main__":
    main()
