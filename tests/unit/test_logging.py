"""
Unit tests for logging module
"""

import pytest
import logging
import json
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from io import StringIO

from src.andamios_orm.logging import (
    StructuredFormatter,
    PerformanceLoggerAdapter,
    AsyncLogHandler,
    setup_logging,
    get_logger,
    log_async_performance,
    log_sync_performance,
    log_context,
    LoggingConfig,
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG,
    TESTING_CONFIG,
    logger,
    performance_logger
)


class TestStructuredFormatter:
    """Test StructuredFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = StructuredFormatter()
    
    def test_format_basic_record(self):
        """Test formatting basic log record."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        result = self.formatter.format(record)
        
        # Parse JSON result
        log_data = json.loads(result)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42
        assert "timestamp" in log_data
        assert log_data["timestamp"].endswith("Z")
    
    def test_format_record_with_exception(self):
        """Test formatting log record with exception."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = True
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        result = self.formatter.format(record)
        log_data = json.loads(result)
        
        assert "exception" in log_data
        assert "ValueError: Test exception" in log_data["exception"]
    
    def test_format_record_with_extra_fields(self):
        """Test formatting log record with extra fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.custom_field = "custom_value"
        record.operation = "test_operation"
        
        result = self.formatter.format(record)
        log_data = json.loads(result)
        
        assert log_data["custom_field"] == "custom_value"
        assert log_data["operation"] == "test_operation"
    
    def test_format_excludes_standard_fields(self):
        """Test that standard LogRecord fields are excluded from extra fields."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        result = self.formatter.format(record)
        log_data = json.loads(result)
        
        # These fields should not appear as separate keys
        excluded_fields = ["name", "msg", "args", "levelname", "levelno", "pathname",
                          "filename", "created", "msecs", "relativeCreated", "thread",
                          "threadName", "processName", "process", "getMessage"]
        
        for field in excluded_fields:
            assert field not in log_data or field in ["module", "function", "line"]


class TestPerformanceLoggerAdapter:
    """Test PerformanceLoggerAdapter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.adapter = PerformanceLoggerAdapter(self.mock_logger)
    
    def test_init(self):
        """Test adapter initialization."""
        assert self.adapter.logger == self.mock_logger
        assert self.adapter.extra == {}
        assert self.adapter._timers == {}
    
    def test_init_with_extra(self):
        """Test adapter initialization with extra data."""
        extra = {"component": "test"}
        adapter = PerformanceLoggerAdapter(self.mock_logger, extra)
        
        assert adapter.extra == extra
    
    def test_process(self):
        """Test process method."""
        msg, kwargs = self.adapter.process("test message", {"key": "value"})
        
        assert msg == "test message"
        assert kwargs == {"key": "value"}
    
    def test_timer_context_manager(self):
        """Test timer context manager."""
        with patch('time.perf_counter', side_effect=[0.0, 1.5]):
            with self.adapter.timer("test_operation"):
                pass
            
            # Should have called debug and info
            assert self.mock_logger.debug.called
            assert self.mock_logger.info.called
            
            # Check info call for completion
            info_calls = self.mock_logger.info.call_args_list
            assert len(info_calls) >= 1
            
            # Last call should be completion
            last_call = info_calls[-1]
            assert "Operation completed: test_operation" in last_call[0][0]
            assert "operation" in last_call[1]["extra"]
            assert "elapsed_time" in last_call[1]["extra"]
            assert last_call[1]["extra"]["elapsed_time"] == 1.5
    
    def test_timer_context_manager_with_exception(self):
        """Test timer context manager with exception."""
        with patch('time.perf_counter', side_effect=[0.0, 1.0]):
            with pytest.raises(ValueError):
                with self.adapter.timer("test_operation"):
                    raise ValueError("Test error")
            
            # Should still log completion even with exception
            assert self.mock_logger.debug.called
            assert self.mock_logger.info.called
    
    def test_start_timer(self):
        """Test start_timer method."""
        with patch('time.perf_counter', return_value=123.45):
            self.adapter.start_timer("operation1")
            
            assert "operation1" in self.adapter._timers
            assert self.adapter._timers["operation1"] == 123.45
            self.mock_logger.debug.assert_called_once()
    
    def test_end_timer_success(self):
        """Test end_timer method with existing timer."""
        self.adapter._timers["operation1"] = 100.0
        
        with patch('time.perf_counter', return_value=101.5):
            elapsed = self.adapter.end_timer("operation1")
            
            assert elapsed == 1.5
            assert "operation1" not in self.adapter._timers
            self.mock_logger.info.assert_called_once()
            
            # Check the info call
            call_args = self.mock_logger.info.call_args
            assert "Timer ended: operation1" in call_args[0][0]
            assert call_args[1]["extra"]["elapsed_time"] == 1.5
    
    def test_end_timer_not_started(self):
        """Test end_timer method with non-existent timer."""
        elapsed = self.adapter.end_timer("nonexistent")
        
        assert elapsed == 0.0
        self.mock_logger.warning.assert_called_once()
        assert "Timer 'nonexistent' was not started" in self.mock_logger.warning.call_args[0][0]


class TestAsyncLogHandler:
    """Test AsyncLogHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.base_handler = Mock(spec=logging.Handler)
        self.base_handler.level = logging.INFO
        self.base_handler.formatter = Mock()
        self.async_handler = AsyncLogHandler(self.base_handler)
    
    def test_init(self):
        """Test async handler initialization."""
        assert self.async_handler.base_handler == self.base_handler
        assert self.async_handler.level == self.base_handler.level
        assert self.async_handler.formatter == self.base_handler.formatter
    
    def test_emit_sync_context(self):
        """Test emit in synchronous context."""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test", args=(), exc_info=None
        )
        
        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")):
            self.async_handler.emit(record)
            
            # Should call base handler directly
            self.base_handler.emit.assert_called_once_with(record)
    
    @pytest.mark.asyncio
    async def test_emit_async_context(self):
        """Test emit in async context."""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test", args=(), exc_info=None
        )
        
        loop = asyncio.get_running_loop()
        with patch.object(loop, 'run_in_executor') as mock_executor:
            mock_executor.return_value = asyncio.Future()
            mock_executor.return_value.set_result(None)
            
            self.async_handler.emit(record)
            
            # Should schedule execution in thread pool
            mock_executor.assert_called_once()
    
    def test_emit_sync_method(self):
        """Test _emit_sync method."""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test", args=(), exc_info=None
        )
        
        self.async_handler._emit_sync(record)
        
        self.base_handler.emit.assert_called_once_with(record)
    
    def test_emit_sync_method_with_exception(self):
        """Test _emit_sync method with exception."""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test", args=(), exc_info=None
        )
        
        self.base_handler.emit.side_effect = Exception("Handler error")
        
        with patch.object(self.async_handler, 'handleError') as mock_handle_error:
            self.async_handler._emit_sync(record)
            
            mock_handle_error.assert_called_once_with(record)


class TestSetupLogging:
    """Test setup_logging function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing handlers
        root_logger = logging.getLogger("andamios_orm")
        root_logger.handlers.clear()
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clear handlers after each test
        root_logger = logging.getLogger("andamios_orm")
        root_logger.handlers.clear()
    
    @patch('src.andamios_orm.logging.logging.StreamHandler')
    def test_setup_logging_basic(self, mock_stream_handler):
        """Test basic logging setup."""
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler
        
        setup_logging(level="DEBUG", format_type="standard")
        
        root_logger = logging.getLogger("andamios_orm")
        assert root_logger.level == logging.DEBUG
        mock_stream_handler.assert_called_once()
        mock_handler.setLevel.assert_called_with(logging.DEBUG)
    
    @patch('src.andamios_orm.logging.logging.StreamHandler')
    def test_setup_logging_structured_format(self, mock_stream_handler):
        """Test logging setup with structured format."""
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler
        
        setup_logging(format_type="structured")
        
        # Should use StructuredFormatter
        assert mock_handler.setFormatter.called
        formatter_arg = mock_handler.setFormatter.call_args[0][0]
        assert isinstance(formatter_arg, StructuredFormatter)
    
    @patch('src.andamios_orm.logging.logging.StreamHandler')
    def test_setup_logging_json_format(self, mock_stream_handler):
        """Test logging setup with JSON format."""
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler
        
        setup_logging(format_type="json")
        
        # Should use StructuredFormatter
        assert mock_handler.setFormatter.called
        formatter_arg = mock_handler.setFormatter.call_args[0][0]
        assert isinstance(formatter_arg, StructuredFormatter)
    
    def test_setup_logging_with_file(self, temp_dir):
        """Test logging setup with file handler."""
        log_file = temp_dir / "test.log"
        
        with patch('src.andamios_orm.logging.logging.handlers.RotatingFileHandler') as mock_file_handler:
            mock_handler = Mock()
            mock_file_handler.return_value = mock_handler
            
            setup_logging(log_file=str(log_file), max_file_size=1024, backup_count=3)
            
            mock_file_handler.assert_called_once_with(
                log_file, maxBytes=1024, backupCount=3
            )
    
    def test_setup_logging_async_mode(self):
        """Test logging setup with async mode."""
        with patch('src.andamios_orm.logging.logging.StreamHandler') as mock_stream_handler:
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            setup_logging(async_mode=True)
            
            root_logger = logging.getLogger("andamios_orm")
            # Should have AsyncLogHandler wrapping the base handler
            assert len(root_logger.handlers) > 0
            handler = root_logger.handlers[0]
            assert isinstance(handler, AsyncLogHandler)
    
    def test_setup_logging_sync_mode(self):
        """Test logging setup with sync mode."""
        with patch('src.andamios_orm.logging.logging.StreamHandler') as mock_stream_handler:
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            setup_logging(async_mode=False)
            
            root_logger = logging.getLogger("andamios_orm")
            # Should use base handler directly
            assert len(root_logger.handlers) > 0
            handler = root_logger.handlers[0]
            assert not isinstance(handler, AsyncLogHandler)
    
    def test_setup_logging_extra_loggers(self):
        """Test logging setup with extra loggers."""
        extra_loggers = ["test_logger1", "test_logger2"]
        
        setup_logging(extra_loggers=extra_loggers, level="WARNING")
        
        for logger_name in extra_loggers:
            logger_obj = logging.getLogger(logger_name)
            assert logger_obj.level == logging.WARNING
    
    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        root_logger = logging.getLogger("andamios_orm")
        
        # Add a dummy handler
        dummy_handler = Mock()
        root_logger.addHandler(dummy_handler)
        assert len(root_logger.handlers) == 1
        
        setup_logging()
        
        # Dummy handler should be cleared
        assert dummy_handler not in root_logger.handlers


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_logger_basic(self):
        """Test basic logger retrieval."""
        logger_obj = get_logger("test_module")
        
        assert isinstance(logger_obj, logging.Logger)
        assert logger_obj.name == "andamios_orm.test_module"
    
    def test_get_logger_performance(self):
        """Test performance logger retrieval."""
        logger_obj = get_logger("test_module", performance=True)
        
        assert isinstance(logger_obj, PerformanceLoggerAdapter)
        assert logger_obj.logger.name == "andamios_orm.test_module"
    
    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "andamios_orm.module1"
        assert logger2.name == "andamios_orm.module2"
        assert logger1 != logger2


class TestPerformanceDecorators:
    """Test performance logging decorators."""
    
    @pytest.mark.asyncio
    async def test_log_async_performance(self):
        """Test async performance decorator."""
        with patch('src.andamios_orm.logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.timer = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            @log_async_performance("test_operation")
            async def test_func():
                return "result"
            
            result = await test_func()
            
            assert result == "result"
            mock_get_logger.assert_called_once_with("performance", performance=True)
            mock_logger.timer.assert_called_once_with("test_operation")
    
    def test_log_sync_performance(self):
        """Test sync performance decorator."""
        with patch('src.andamios_orm.logging.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.timer = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            @log_sync_performance("test_operation")
            def test_func():
                return "result"
            
            result = test_func()
            
            assert result == "result"
            mock_get_logger.assert_called_once_with("performance", performance=True)
            mock_logger.timer.assert_called_once_with("test_operation")


class TestLogContext:
    """Test log_context context manager."""
    
    def test_log_context_success(self):
        """Test log_context with successful operation."""
        mock_logger = Mock()
        
        with patch('time.perf_counter', side_effect=[0.0, 1.5]):
            with log_context(mock_logger, "test_operation", user_id=123):
                pass
            
            # Should log start and completion
            assert mock_logger.info.call_count == 2
            
            # Check calls
            calls = mock_logger.info.call_args_list
            start_call, end_call = calls
            
            assert "Starting test_operation" in start_call[0][0]
            assert start_call[1]["extra"]["user_id"] == 123
            
            assert "Completed test_operation" in end_call[0][0]
            assert end_call[1]["extra"]["user_id"] == 123
            assert end_call[1]["extra"]["elapsed_time"] == 1.5
            assert end_call[1]["extra"]["success"] is True
    
    def test_log_context_exception(self):
        """Test log_context with exception."""
        mock_logger = Mock()
        
        with patch('time.perf_counter', side_effect=[0.0, 1.0]):
            with pytest.raises(ValueError):
                with log_context(mock_logger, "test_operation", user_id=123):
                    raise ValueError("Test error")
            
            # Should log start and failure
            assert mock_logger.info.call_count == 1  # Only start
            assert mock_logger.error.call_count == 1  # Failure
            
            error_call = mock_logger.error.call_args
            assert "Failed test_operation: Test error" in error_call[0][0]
            assert error_call[1]["extra"]["success"] is False
            assert error_call[1]["extra"]["error"] == "Test error"


class TestLoggingConfig:
    """Test LoggingConfig class."""
    
    def test_logging_config_init(self):
        """Test LoggingConfig initialization."""
        config = LoggingConfig(
            level="WARNING",
            format_type="json",
            log_file="/path/to/log",
            async_mode=False,
            performance_logging=True
        )
        
        assert config.level == "WARNING"
        assert config.format_type == "json"
        assert config.log_file == "/path/to/log"
        assert config.async_mode is False
        assert config.performance_logging is True
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig with default values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.format_type == "standard"
        assert config.log_file is None
        assert config.async_mode is True
        assert config.performance_logging is False
    
    def test_logging_config_apply(self):
        """Test LoggingConfig apply method."""
        config = LoggingConfig(level="DEBUG", performance_logging=True)
        
        with patch('src.andamios_orm.logging.setup_logging') as mock_setup:
            config.apply()
            
            mock_setup.assert_called_once_with(
                level="DEBUG",
                format_type="standard",
                log_file=None,
                async_mode=True,
                extra_loggers=["andamios_orm.performance"]
            )
    
    def test_logging_config_apply_no_performance(self):
        """Test LoggingConfig apply without performance logging."""
        config = LoggingConfig(performance_logging=False)
        
        with patch('src.andamios_orm.logging.setup_logging') as mock_setup:
            config.apply()
            
            mock_setup.assert_called_once_with(
                level="INFO",
                format_type="standard",
                log_file=None,
                async_mode=True,
                extra_loggers=[]
            )


class TestPredefinedConfigs:
    """Test predefined logging configurations."""
    
    def test_development_config(self):
        """Test DEVELOPMENT_CONFIG values."""
        assert DEVELOPMENT_CONFIG.level == "DEBUG"
        assert DEVELOPMENT_CONFIG.format_type == "standard"
        assert DEVELOPMENT_CONFIG.async_mode is True
        assert DEVELOPMENT_CONFIG.performance_logging is True
    
    def test_production_config(self):
        """Test PRODUCTION_CONFIG values."""
        assert PRODUCTION_CONFIG.level == "INFO"
        assert PRODUCTION_CONFIG.format_type == "json"
        assert PRODUCTION_CONFIG.log_file == "/var/log/andamios-orm/app.log"
        assert PRODUCTION_CONFIG.async_mode is True
        assert PRODUCTION_CONFIG.performance_logging is False
    
    def test_testing_config(self):
        """Test TESTING_CONFIG values."""
        assert TESTING_CONFIG.level == "WARNING"
        assert TESTING_CONFIG.format_type == "standard"
        assert TESTING_CONFIG.async_mode is False
        assert TESTING_CONFIG.performance_logging is False


class TestModuleGlobals:
    """Test module-level globals."""
    
    def test_default_logger(self):
        """Test default logger is properly configured."""
        assert isinstance(logger, logging.Logger)
        assert logger.name == "andamios_orm.core"
    
    def test_performance_logger(self):
        """Test performance logger is properly configured."""
        assert isinstance(performance_logger, PerformanceLoggerAdapter)
        assert performance_logger.logger.name == "andamios_orm.performance"


class TestLoggingIntegration:
    """Integration tests for logging functionality."""
    
    def test_structured_logging_integration(self):
        """Test structured logging end-to-end."""
        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        test_logger = logging.getLogger("test_integration")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)
        
        # Log a message with extra data
        test_logger.info("Test message", extra={"user_id": 123, "operation": "test"})
        
        # Parse output
        output = log_stream.getvalue()
        log_data = json.loads(output.strip())
        
        assert log_data["message"] == "Test message"
        assert log_data["user_id"] == 123
        assert log_data["operation"] == "test"
        assert log_data["level"] == "INFO"
    
    @pytest.mark.asyncio
    async def test_performance_logging_integration(self):
        """Test performance logging end-to-end."""
        perf_logger = get_logger("test_perf", performance=True)
        
        # Capture calls to underlying logger
        with patch.object(perf_logger.logger, 'info') as mock_info:
            with patch.object(perf_logger.logger, 'debug') as mock_debug:
                with patch('time.perf_counter', side_effect=[0.0, 0.5]):
                    with perf_logger.timer("test_operation"):
                        await asyncio.sleep(0.001)  # Simulate work
                    
                    mock_debug.assert_called_once()
                    mock_info.assert_called_once()
                    
                    info_call = mock_info.call_args
                    assert "Operation completed: test_operation" in info_call[0][0]
                    assert info_call[1]["extra"]["elapsed_time"] == 0.5