#!/usr/bin/env python3
import argparse
import gc
import os
import sys
from dataclasses import dataclass
from typing import Optional, List, Tuple
import weakref
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
        print(color(f"Deleting {self.name}", YELLOW))


def make_cycle_pair(a_name: str, b_name: str) -> List[Node]:
    a = Node(a_name)
    b = Node(b_name)
    a.other = b
    b.other = a
    return [a, b]


def break_cycle(nodes: List[Node]) -> None:
    for node in nodes:
        node.other = None


def weakref_demo() -> Tuple[weakref.ReferenceType, weakref.ReferenceType]:
    a = Node("Weak-A")
    b = Node("Weak-B")
    a_ref = weakref.ref(a)
    b_ref = weakref.ref(b)
    a.other = None
    b.other = None
    return a_ref, b_ref


@contextmanager
def temporary_gc_debug(flags: int):
    prev = gc.get_debug()
    gc.set_debug(flags)
    try:
        yield
    finally:
        gc.set_debug(prev)


def main():
    parser = argparse.ArgumentParser(description="Python GC cycle demonstration")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles to create")
    parser.add_argument("--saveall", action="store_true", help="Use DEBUG_SAVEALL to keep uncollectable objects in gc.garbage")
    parser.add_argument("--no-debug", action="store_true", help="Disable GC debug logs")
    parser.add_argument("--break-cycles", action="store_true", help="Break cycles before collection")
    parser.add_argument("--weakref-demo", action="store_true", help="Run weakref demonstration")
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

    debug_flags = 0 if args.no_debug else gc.DEBUG_LEAK | (gc.DEBUG_SAVEALL if args.saveall else 0)

    print(color(f"Creating {args.cycles} cycle(s)...", BOLD, CYAN))
    holders: List[List[Node]] = []
    for i in range(args.cycles):
        pair = make_cycle_pair(f"A{i}", f"B{i}")
        holders.append(pair)

    if args.break_cycles:
        print(color("Breaking cycles before collection...", YELLOW))
        for pair in holders:
            break_cycle(pair)

    # Drop strong refs from our local list to simulate out-of-scope variables
    print(color("Dropping local references to cycles...", CYAN))
    holders = []

    if args.weakref_demo:
        print(color("Running weakref demo...", BLUE))
        aref, bref = weakref_demo()
        print(color(f"Weakrefs alive? A={aref() is not None} B={bref() is not None}", BLUE))

    with temporary_gc_debug(debug_flags):
        print(color("\nCollecting garbage...", MAGENTA))
        collected = gc.collect()
        print(color(f"GC collected {collected} unreachable objects.", GREEN if collected else BLUE))

        if args.saveall and gc.garbage:
            print(color(f"Uncollectable retained in gc.garbage: {len(gc.garbage)}", RED, BOLD))
            for idx, obj in enumerate(gc.garbage[:10], 1):
                print(color(f"  [{idx}] type={type(obj).__name__} repr={repr(obj)}", RED))

        gen_stats = getattr(gc, "get_stats", None)
        if callable(gen_stats):
            stats = gc.get_stats()
            print(color("Generation stats:", BOLD))
            for gen, s in enumerate(stats):
                print(
                    color(
                        f"  Gen {gen}: collections={s['collections']} collected={s['collected']} uncollectable={s['uncollectable']}",
                        CYAN,
                    )
                )


if __name__ == "__main__":
    main()
