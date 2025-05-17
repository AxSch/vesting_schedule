import asyncio
import csv
import os
from datetime import datetime
from decimal import InvalidOperation, Decimal
from io import StringIO
from typing import List

from exceptions.parser_exceptions import CSVParserError
from models.event import Event, EventType
from utils.decimal_utils import format_decimal


class CSVProcessor:
    def __init__(self, chunk_size: int = 5000, max_workers: int = 1):
        self.chunk_size = chunk_size
        self.max_workers = max_workers

    @staticmethod
    def _parse_row(row: List[str], line_number: int, precision: int) -> Event:
        if precision is None:
            precision = 0

        if len(row) != 6:
            raise CSVParserError(f"Expected 6 fields, got {len(row)}", line_number)

        try:
            event_type_str = row[0].strip() if row[0] is not None else ""
            if not event_type_str:
                raise CSVParserError("Event type cannot be empty", line_number)

            try:
                event_type = EventType(event_type_str)
            except ValueError:
                raise CSVParserError(f"Invalid event type: {event_type_str}", line_number)
        except AttributeError:
            raise CSVParserError(f"Invalid event type: {row[0]}", line_number)

        employee_id = row[1] if row[1] is not None else ""
        employee_name = row[2] if row[2] is not None else ""
        award_id = row[3] if row[3] is not None else ""

        if not employee_id or not employee_name or not award_id:
            raise CSVParserError("Employee ID, name, and award ID cannot be empty", line_number)

        try:
            date_str = row[4].strip() if row[4] is not None else ""
            if not date_str:
                raise CSVParserError("Event date cannot be empty", line_number)

            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise CSVParserError(
                    f"Invalid event date: '{date_str}' expected YYYY-MM-DD", line_number
                )
        except AttributeError:
            raise CSVParserError(f"Invalid event date: {row[4]}", line_number)

        try:
            quantity_str = row[5].strip() if row[5] is not None else ""
            if not quantity_str:
                raise CSVParserError("Quantity cannot be empty", line_number)

            try:
                quantity = Decimal(quantity_str)
                if quantity is None or quantity <= 0:
                    raise CSVParserError(f"Quantity must be positive, got {quantity}", line_number)
                quantity = format_decimal(quantity, precision)
            except (InvalidOperation, TypeError) as e:
                raise CSVParserError(
                    f"Invalid quantity: {row[5]}, Error: {str(e)}", line_number
                )
        except AttributeError:
            raise CSVParserError(f"Invalid quantity: {row[5]}", line_number)

        return Event(
            event_type=event_type,
            employee_id=employee_id,
            employee_name=employee_name,
            award_id=award_id,
            event_date=event_date,
            quantity=quantity
        )

    def _process_chunk_sync(self, lines: List[str], start_line: int, precision: int) -> List[Event]:
        events = []

        if start_line is None:
            start_line = 0

        if precision is None:
            precision = 0

        try:
            reader = csv.reader(StringIO('\n'.join(lines)))

            for i, row in enumerate(reader, start=start_line):
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                try:
                    event = self._parse_row(row, i, precision)
                    events.append(event)
                except Exception as error:
                    raise CSVParserError(f"Error parsing line {i}: {error}")
        except Exception as e:
            raise CSVParserError(f"Error processing chunk: {str(e)}")

        return events

    async def parse_csv(self, file_path: str, precision: int = 0) -> List[Event]:
        if not os.path.exists(file_path):
            raise CSVParserError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', newline='') as file:
                content = file.read()

            lines = content.split('\n')
            chunks = [lines[i:i + self.chunk_size] for i in range(0, len(lines), self.chunk_size)]

            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = []

            for i, chunk in enumerate(chunks):
                start_line = i * self.chunk_size
                task = self.process_chunk(semaphore, chunk, start_line, precision)
                tasks.append(task)

            chunk_results = await asyncio.gather(*tasks)
            return [event for chunk in chunk_results for event in chunk]

        except Exception as error:
            raise CSVParserError(f"Error parsing CSV: {error}")

    async def process_chunk(self, semaphore, lines: List[str], start_line: int, precision: int) -> List[Event]:
        async with semaphore:
            return await asyncio.to_thread(self._process_chunk_sync, lines, start_line, precision)
