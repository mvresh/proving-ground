import sys
import argparse
from utils import format_error
import commands

def main():
    parser = argparse.ArgumentParser(
        description="Proving Ground: Order-book Manipulation Detection Benchmark",
        exit_on_error=False
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    gen_parser = subparsers.add_parser("generate")
    gen_parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic generation")
    gen_parser.add_argument("--events", type=int, default=100, help="Approximate number of events")
    gen_parser.add_argument("--market", type=str, default="SUI/USDC", help="Market identifier")

    # Inject command
    inj_parser = subparsers.add_parser("inject")
    inj_parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic injection")

    # Generate-set command
    set_parser = subparsers.add_parser("generate-set")
    set_parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic generation")
    set_parser.add_argument("--count", type=int, default=10, help="Number of scenarios to generate")
    set_parser.add_argument("--manipulated-fraction", type=float, default=0.3, help="Fraction of manipulated scenarios")
    set_parser.add_argument("--market", type=str, default="SUI/USDC", help="Market identifier")
    set_parser.add_argument("--events", type=int, default=50, help="Events per scenario")

    # Detect command
    det_parser = subparsers.add_parser("detect")
    det_parser.add_argument("--detector", type=str, default="heuristic", choices=["heuristic", "llm"])
    det_parser.add_argument("--provider", type=str, default="stub", choices=["stub", "flock"])

    # Score command
    subparsers.add_parser("score")

    # Models command
    models_parser = subparsers.add_parser("models")
    models_parser.add_argument("--provider", type=str, default="stub", choices=["stub", "flock"])

    # Run command
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--count", type=int, default=10)
    run_parser.add_argument("--manipulated-fraction", type=float, default=0.3)
    run_parser.add_argument("--market", type=str, default="SUI/USDC")
    run_parser.add_argument("--events", type=int, default=50)
    run_parser.add_argument("--detector-id", type=str, default="heuristic_v1")

    # Benchmark command
    bench_parser = subparsers.add_parser("benchmark")
    bench_parser.add_argument("--seed", type=int, default=42)
    bench_parser.add_argument("--count", type=int, default=10)
    bench_parser.add_argument("--manipulated-fraction", type=float, default=0.3)
    bench_parser.add_argument("--market", type=str, default="SUI/USDC")
    bench_parser.add_argument("--events", type=int, default=50)
    bench_parser.add_argument("--provider", type=str, default="stub", choices=["stub", "flock"])

    # Attest command
    attest_parser = subparsers.add_parser("attest")
    attest_parser.add_argument("--store", type=str, default="stub", choices=["stub", "walrus"])

    # Verify command
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--store", type=str, default="stub", choices=["stub", "walrus"])

    try:
        args = parser.parse_args()
        if args.command == "generate":
            commands.cmd_generate(args)
        elif args.command == "inject":
            commands.cmd_inject(args)
        elif args.command == "generate-set":
            commands.cmd_generate_set(args)
        elif args.command == "detect":
            commands.cmd_detect(args)
        elif args.command == "score":
            commands.cmd_score(args)
        elif args.command == "run":
            commands.cmd_run(args)
        elif args.command == "benchmark":
            commands.cmd_benchmark(args)
        elif args.command == "attest":
            commands.cmd_attest(args)
        elif args.command == "verify":
            commands.cmd_verify(args)
        elif args.command == "models":
            commands.cmd_models(args)
        else:
            print(format_error("CLI", f"Unknown command: {args.command}"), file=sys.stderr)
            sys.exit(1)
    except argparse.ArgumentError as e:
        print(format_error("CLI", str(e)), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(format_error("FATAL", f"An unexpected error occurred: {str(e)}"), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()