"""Unit tests for built-in tools."""

import pytest
from tools import CalculatorTool, FileSystemTool


class TestCalculator:
    def setup_method(self):
        self.calc = CalculatorTool()

    def test_addition(self):
        assert self.calc.run("2 + 3") == "5"

    def test_complex_expression(self):
        assert self.calc.run("(10 * 3) + (200 / 4)") == "80.0"

    def test_power(self):
        assert self.calc.run("2 ** 10") == "1024"

    def test_negative(self):
        assert self.calc.run("-5 + 3") == "-2"

    def test_division_by_zero(self):
        result = self.calc.run("1 / 0")
        assert "Error" in result


class TestFileSystem:
    def setup_method(self):
        self.fs = FileSystemTool(base_dir="/tmp/agent_test")

    def test_write_and_read(self):
        self.fs.run('{"action": "write", "path": "test.txt", "content": "hello world"}')
        result = self.fs.run('{"action": "read", "path": "test.txt"}')
        assert result == "hello world"

    def test_exists(self):
        self.fs.run('{"action": "write", "path": "exists.txt", "content": "x"}')
        result = self.fs.run('{"action": "exists", "path": "exists.txt"}')
        assert result == "True"

    def test_not_exists(self):
        result = self.fs.run('{"action": "exists", "path": "nope.txt"}')
        assert result == "False"

    def test_invalid_json(self):
        result = self.fs.run("not json")
        assert "Error" in result
