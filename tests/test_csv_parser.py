import os
import tempfile
from datetime import date
from decimal import Decimal
import pytest

from utils.csv_parser import parse_csv
from exceptions.parser_exceptions import CSVParserError
from models.event import EventType

class TestCSVParser:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".csv")

    def teardown_method(self):
        os.unlink(self.temp_file.name)

    def test_parse_csv_file_not_found(self):
        with pytest.raises(CSVParserError, match="File not found"):
            parse_csv("non_existent_file.csv")

    def test_parse_csv(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,2020-01-01,1000\n")
        self.temp_file.write("VEST,E001,Alice Smith,ISO-002,2020-02-01,500\n")
        self.temp_file.flush()

        events = parse_csv(self.temp_file.name)

        assert len(events) == 2

        assert events[0].event_type == EventType.VEST
        assert events[0].employee_id == "E001"
        assert events[0].employee_name == "Alice Smith"
        assert events[0].award_id == "ISO-001"
        assert events[0].event_date == date(2020, 1, 1)
        assert events[0].quantity == Decimal("1000")

        assert events[1].event_type == EventType.VEST
        assert events[1].employee_id == "E001"
        assert events[1].employee_name == "Alice Smith"
        assert events[1].award_id == "ISO-002"
        assert events[1].event_date == date(2020, 2, 1)
        assert events[1].quantity == Decimal("500")

    def test_parse_csv_with_cancel_events(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,2020-01-01,1000\n")
        self.temp_file.write("CANCEL,E001,Alice Smith,ISO-001,2020-02-01,300\n")
        self.temp_file.flush()

        events = parse_csv(self.temp_file.name)

        assert len(events) == 2
        assert events[0].event_type == EventType.VEST
        assert events[1].event_type == EventType.CANCEL
        assert events[1].quantity == Decimal("300")

    def test_parse_csv_invalid_row_format(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,2020-01-01\n")
        self.temp_file.flush()

        with pytest.raises(CSVParserError, match="Expected 6 fields"):
            parse_csv(self.temp_file.name)

    def test_parse_csv_invalid_event_type(self):
        self.temp_file.write("INVALID,E001,Alice Smith,ISO-001,2020-01-01,1000\n")
        self.temp_file.flush()

        with pytest.raises(CSVParserError, match="Invalid event type"):
            parse_csv(self.temp_file.name)

    def test_parse_csv_invalid_date_format(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,01/01/2020,1000\n")
        self.temp_file.flush()

        with pytest.raises(CSVParserError, match="Invalid event date: '01/01/2020' expected YYYY-MM-DD"):
            parse_csv(self.temp_file.name)

    def test_parse_csv_invalid_quantity(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,2020-01-01,abc\n")
        self.temp_file.flush()

        with pytest.raises(CSVParserError, match="Invalid quantity"):
            parse_csv(self.temp_file.name)

    def test_parse_csv_negative_quantity(self):
        self.temp_file.write("VEST,E001,Alice Smith,ISO-001,2020-01-01,-1000\n")
        self.temp_file.flush()

        with pytest.raises(CSVParserError, match="Quantity must be positive"):
            parse_csv(self.temp_file.name)
