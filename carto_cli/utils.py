"""
General purpose functions can be stored here.
"""

import sys

def check_piped_arg(ctx, main_arg, arg_label='job ID'):
    if main_arg:
        return main_arg
    else:
        if not sys.stdin.isatty():
            return sys.stdin.read().rstrip()
        else:
            n = 'n' if arg_label[0].lower() in ['a','e','i','o','u'] else ''
            ctx.fail(
                f"A{n} {arg_label} is required. "
                "Either pass it explicitly or pipe into the command"
            )
