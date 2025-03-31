import csv
import io
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Iterator

from exceptions.parser_exceptions import CSVParserError
from models.event import Event, EventType
from utils.decimal_utils import format_decimal
from utils.concurrency_utils import parallel_map


class CSVProcessor:
    def __init__(self, chunk_size: int = 5000, max_workers: int = 1):
        self.chunk_size = chunk_size
        self.max_workers = max_workers

    @staticmethod
    def _parse_row(row: List[str], line_number: int, precision: int) -> Event:
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
            raise CSVParserError(
                f"Invalid event date: '{row[4]}' expected YYYY-MM-DD", line_number
            )

        try:
            quantity = Decimal(row[5])
            if quantity <= 0:
                raise CSVParserError(
                    f"Quantity must be positive, got {quantity}", line_number
                )
            quantity = format_decimal(quantity, precision)
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

    @staticmethod
    def _count_file_lines(file_path: str) -> int:
        with open(file_path, 'rb') as csv_file:
            return sum(1 for line in csv_file)

    def _process_chunk(self, chunk: List[List[str]], start_line: int, precision: int) -> List[Event]:
        events = []
        for item, row in enumerate(chunk, start=start_line):
            try:
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                event = self._parse_row(row, item, precision)
                events.append(event)
            except Exception as error:
                raise CSVParserError(f"Processing of invalid chunk: {error} - {row}")
        return events

    def _split_file_into_chunks(self, file_path: str) -> List[Dict]:
        total_lines = self._count_file_lines(file_path)
        chunk_count = max(1, total_lines // self.chunk_size)

        chunks = []
        with open(file_path, 'r', newline='') as csv_file:
            for chunk in range(chunk_count):
                start_pos = csv_file.tell()
                lines = []

                for item in range(self.chunk_size):
                    line = csv_file.readline()
                    if not line:
                        break
                    lines.append(line)

                if lines:
                    chunks.append({
                        'start_pos': start_pos,
                        'lines': lines,
                        'start_line': chunk * self.chunk_size + 1
                    })
        return chunks

    def _process_file_chunk(self, chunk: Dict, precision: int) -> List[Event]:
        reader = csv.reader(io.StringIO(''.join(chunk['lines'])))
        rows = list(reader)
        return self._process_chunk(rows, chunk['start_line'], precision)

    def parallel_process_csv(self, file_path: str, precision: int = 0) -> List[Event]:
        if not os.path.exists(file_path):
            raise CSVParserError(f"File not found: {file_path}")

        try:
            chunks = self._split_file_into_chunks(file_path)
            all_events = parallel_map(
                lambda chunk: self._process_file_chunk(chunk, precision),
                chunks,
                max_workers=self.max_workers if self.max_workers and self.max_workers > 0 else None
            )
            return [event for chunk_events in all_events for event in chunk_events]

        except Exception as error:
            raise CSVParserError(f"Error during CSV processing: {error}")

    def stream_parse_csv(self, file_path: str, precision: int = 0) -> Iterator[Event]:
        if not os.path.exists(file_path):
            raise CSVParserError(f"File not found: {file_path}")
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                batch = []

                for line_number, row in enumerate(reader, 1):
                    if not row or all(cell.strip() == "" for cell in row):
                        continue
                    try:
                        event = self._parse_row(row, line_number, precision)
                        batch.append(event)
                    except Exception as error:
                        raise CSVParserError(f"Unexpected error parsing row: {error}")

                    if len(batch) >= self.chunk_size:
                        yield from batch
                        batch = []

                if batch:
                    yield from batch
        except Exception as error:
            raise CSVParserError(f"Unexpected error: {error}")

def parse_csv(csv_file: str, precision: int = 0, use_parallel: bool = True,
              max_workers: int = None, chunk_size: int = 5000) -> List[Event]:
    processor = CSVProcessor(chunk_size=chunk_size, max_workers=max_workers)
    try:
        if use_parallel:
            return processor.parallel_process_csv(csv_file, precision)
        else:
            return list(processor.stream_parse_csv(csv_file, precision))
    except CSVParserError:
        raise
    except Exception as error:
        raise CSVParserError(f"Unexpected error: {error}")
