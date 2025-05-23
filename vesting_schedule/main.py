import sys
import argparse
from datetime import datetime

from exceptions.parser_exceptions import CSVParserError
from exceptions.vesting_exception import VestingValidationError
from utils.csv_parser import parse_csv
from services.vesting_service import VestingService


def main():
    parser = argparse.ArgumentParser(description='Vesting schedule to show vested shares at a given time')
    parser.add_argument('file', help='CSV file containing vesting events')
    parser.add_argument('date', help='Target date in YYYY-MM-DD format')
    parser.add_argument('precision', nargs='?', type=int, default=0,
                        help='Number of decimal places to consider (0-6)')
    parser.add_argument('--parallel', action='store_true', help='Use parallel processing')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of worker threads/processes (default: auto)')
    parser.add_argument('--chunk-size', type=int, default=5000,
                        help='Number of rows to process in each chunk (default: 5000)')

    args = parser.parse_args()

    if not (0 <= args.precision <= 6):
        print(f"Error: Precision must be between 0 and 6, got {args.precision}", file=sys.stderr)
        sys.exit(1)

    try:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

        events = parse_csv(
            args.file,
            args.precision,
            use_parallel=args.parallel,
            max_workers=args.workers,
            chunk_size=args.chunk_size
        )

        service = VestingService(use_parallel=args.parallel, max_workers=args.workers)
        service.process_events(events)

        schedule = service.get_vesting_schedule(target_date, args.precision)

        for employee_id, employee_name, award_id, net_vested in schedule:
            if args.precision == 0:
                net_vested_str = str(int(net_vested))
            else:
                format_str = f"{{:.{args.precision}f}}"
                net_vested_str = format_str.format(float(net_vested))
                if float(net_vested) == 0:
                    net_vested_str = format_str.format(0)

            print(f"{employee_id},{employee_name},{award_id},{net_vested_str}")

    except CSVParserError as error:
        print(f"Error parsing CSV: {str(error)}", file=sys.stderr)
        sys.exit(1)

    except VestingValidationError as error:
        print(f"Validation error: {str(error)}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"Unexpected error: {str(error)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
