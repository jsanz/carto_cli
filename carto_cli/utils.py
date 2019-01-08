"""
General purpose functions can be stored here.
"""

import sys

def check_piped_arg(ctx, param, value):
    if value:
        return value
    else:
        if not sys.stdin.isatty():
            return sys.stdin.read().rstrip()
        else:
            ctx.fail(
                f"Missing argument: {param.human_readable_name}.\n"
                "Either pass it explicitly or pipe into the command"
            )
