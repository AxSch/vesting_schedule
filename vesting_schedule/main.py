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
                        help='Number of decimal places to consider (0-3)')

    args = parser.parse_args()

    if not (0 <= args.precision <= 3):
        print(f"Error: Precision must be between 0 and 3, got {args.precision}", file=sys.stderr)
        sys.exit(1)

    try:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

        events = parse_csv(args.file, args.precision)

        service = VestingService()
        service.process_events(events)

        schedule = service.get_vesting_schedule(target_date, args.precision)

        for employee_id, employee_name, award_id, net_vested in schedule:
            if args.precision > 0:
                net_vested_str = f"{net_vested:.{args.precision}}"
            else:
                net_vested_str = str(int(net_vested))

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
