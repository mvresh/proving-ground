import sys
import json
from typing import Any
from utils import format_error
import handlers

def cmd_attest(args: Any) -> None:
    """Handles the 'attest' command."""
    try:
        print(handlers.handle_attest(args))
    except Exception as e:
        print(format_error("ATTEST", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_verify(args: Any) -> None:
    """Handles the 'verify' command."""
    try:
        print(handlers.handle_verify(args))
    except Exception as e:
        print(format_error("VERIFY", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_models(args: Any) -> None:
    """Handles the 'models' command."""
    try:
        print(handlers.handle_models(args))
    except Exception as e:
        print(format_error("MODELS", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_score(args: Any) -> None:
    """Handles the 'score' command."""
    try:
        print(handlers.handle_score(args))
    except json.JSONDecodeError as e:
        print(format_error("SCORE", f"Invalid JSON input: {str(e)}"), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(format_error("SCORE", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_detect(args: Any) -> None:
    """Handles the 'detect' command."""
    try:
        print(handlers.handle_detect(args))
    except json.JSONDecodeError as e:
        print(format_error("DETECT", f"Invalid JSON input: {str(e)}"), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(format_error("DETECT", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_generate_set(args: Any) -> None:
    """Handles the 'generate-set' command."""
    try:
        print(handlers.handle_generate_set(args))
    except Exception as e:
        print(format_error("GENERATE-SET", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_generate(args: Any) -> None:
    """Handles the 'generate' command."""
    try:
        print(handlers.handle_generate(args))
    except Exception as e:
        print(format_error("GENERATE", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_run(args: Any) -> None:
    """Handles the 'run' command orchestrating the full benchmark loop."""
    try:
        print(handlers.handle_run(args))
    except Exception as e:
        print(format_error("RUN", f"Benchmark execution failed: {str(e)}"), file=sys.stderr)
        sys.exit(1)

def cmd_inject(args: Any) -> None:
    """Handles the 'inject' command."""
    try:
        print(handlers.handle_inject(args))
    except json.JSONDecodeError as e:
        print(format_error("INJECT", f"Invalid JSON input: {str(e)}"), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(format_error("INJECT", str(e)), file=sys.stderr)
        sys.exit(1)

def cmd_benchmark(args: Any) -> None:
    """Handles the 'benchmark' command comparing Heuristic vs LLM detectors."""
    try:
        print(handlers.handle_benchmark(args))
    except Exception as e:
        print(format_error("BENCHMARK", f"Comparison failed: {str(e)}"), file=sys.stderr)
        sys.exit(1)