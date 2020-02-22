import pytest

import logger


def test_log_debug(caplog):
    """Test correct debug message is logged"""
    with caplog.at_level(10):
        msg = 'Test debug'
        logger.log_debug(msg)
        assert msg in caplog.text
        assert 'DEBUG' in caplog.text


def test_log_debug_muted(caplog):
    """Test nothing is logged when log level is above DEBUG"""
    with caplog.at_level(20):
        msg = 'Test debug'
        logger.log_debug(msg)
        assert len(caplog.records) == 0


def test_log_info(caplog):
    """Test correct info message is logged"""
    msg = 'Test info'
    logger.log_info(msg)
    for record in caplog.records:
        assert record.levelname == 'INFO'

    assert msg in caplog.text


def test_log_warning(caplog):
    """Test correct warning message is logged"""
    msg = 'Test warn'
    logger.log_warning(msg)
    assert msg in caplog.text
    assert 'WARNING' in caplog.text


def test_log_error(caplog):
    """Test correct error message is logged"""
    msg = 'Test error'
    logger.log_error(msg)
    assert msg in caplog.text
    assert 'ERROR' in caplog.text


def test_log_exception(caplog):
    """Test correct exception message is logged"""
    msg = 'Test exception'
    logger.log_exception(msg)
    assert msg in caplog.text
    assert 'ERROR' in caplog.text
