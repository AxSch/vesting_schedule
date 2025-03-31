import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List

from exceptions.parser_exceptions import CSVParserError
from models.event import Event, EventType

def parse_event_row(row: List[str], line_number: int, precision: int) -> Event:
    if len(row) != 6:
        raise CSVParserError(f"Expected 6 fields, got {len(row)}", line_number)

    try:
        event_type = EventType(row[0])
    except ValueError:
        raise CSVParserError(f"Invalid event type: {row[0]}", line_number)

    employee_id = row[1]
    employee_name = row[2]
    award_id = row[3]

    try:
        event_date = datetime.strptime(row[4], "%Y-%m-%d").date()
    except ValueError:
        raise CSVParserError(f"Invalid event date: '{row[4]}' expected YYYY-MM-DD", line_number)

    try:
        quantity = Decimal(row[5])
        if quantity <= 0:
            raise CSVParserError(
                f"Quantity must be positive, got {quantity}", line_number
            )

        if precision > 0:
            quantity = quantity.quantize(Decimal(f'0.{"0" * precision}'), rounding='ROUND_DOWN')
        else:
            quantity = quantity.to_integral_exact(rounding='ROUND_DOWN')
    except InvalidOperation:
        raise CSVParserError(
            f"Invalid quantity: {row[5]}", line_number
        )

    return Event(
        event_type=event_type,
        employee_id=employee_id,
        employee_name=employee_name,
        award_id=award_id,
        event_date=event_date,
        quantity=quantity
    )

def parse_csv(csv_file: str, precision: int = 0) -> List[Event]:
    events = []

    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            for line_number, row in enumerate(reader, 1):
                event = parse_event_row(row, line_number, precision)
                events.append(event)

    except FileNotFoundError as error:
        raise CSVParserError(f"File not found: {error}")
    except Exception as error:
        raise CSVParserError(f"Unexpected error: {error}")
    return events
