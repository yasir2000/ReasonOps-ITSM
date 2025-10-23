#!/usr/bin/env python3
"""
ReasonOps CLI Wrapper - Clean interface without startup warnings
"""

import sys
import os
import warnings

# Suppress warnings during imports
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Redirect import warnings to devnull
import io
from contextlib import redirect_stdout, redirect_stderr

with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
    # Import CLI module (this will trigger the optional dependency warnings)
    import cli

# Now run the CLI with normal output
if __name__ == "__main__":
    cli.main()
