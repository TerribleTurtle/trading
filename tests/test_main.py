import pytest
from click.testing import CliRunner

from src.shadow_bot.main import cli

def test_cli_scan_command_wires_dependencies(mocker):
    mock_scanner_run = mocker.patch("src.shadow_bot.main.Scanner.run_once")
    mocker.patch("src.shadow_bot.main.KalshiAdapter")
    mock_repo = mocker.patch("src.shadow_bot.main.SQLiteRepo")
    mocker.patch("src.shadow_bot.main.DiscordAlerter")
    mocker.patch("src.shadow_bot.main.create_engine")
    
    runner = CliRunner()
    result = runner.invoke(cli, ["scan"])
    
    assert result.exit_code == 0
    mock_scanner_run.assert_called_once()
    mock_repo.return_value.setup.assert_called_once()

def test_cli_resolve_command_wires_dependencies(mocker):
    mock_resolve_trades = mocker.patch("src.shadow_bot.main.Resolver.resolve_trades")
    mocker.patch("src.shadow_bot.main.KalshiAdapter")
    mock_repo = mocker.patch("src.shadow_bot.main.SQLiteRepo")
    mocker.patch("src.shadow_bot.main.DiscordAlerter")
    mocker.patch("src.shadow_bot.main.create_engine")
    
    runner = CliRunner()
    result = runner.invoke(cli, ["resolve"])
    
    assert result.exit_code == 0
    mock_resolve_trades.assert_called_once()
    mock_repo.return_value.setup.assert_called_once()

def test_cli_run_command_wires_dependencies_and_loops(mocker):
    mock_scanner_run = mocker.patch("src.shadow_bot.main.Scanner.run_once")
    mock_resolve_trades = mocker.patch("src.shadow_bot.main.Resolver.resolve_trades")
    mock_sleep = mocker.patch("src.shadow_bot.main.time.sleep", side_effect=KeyboardInterrupt)
    
    mocker.patch("src.shadow_bot.main.KalshiAdapter")
    mock_repo = mocker.patch("src.shadow_bot.main.SQLiteRepo")
    mocker.patch("src.shadow_bot.main.DiscordAlerter")
    mocker.patch("src.shadow_bot.main.create_engine")
    
    runner = CliRunner()
    result = runner.invoke(cli, ["run"])
    
    assert result.exit_code == 0
    mock_scanner_run.assert_called_once()
    mock_resolve_trades.assert_called_once()
    mock_sleep.assert_called_once_with(60)
    mock_repo.return_value.setup.assert_called_once()
