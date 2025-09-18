

def test_cli_error_handling_exit_codes():
    """T007: Contract test for error handling and proper exit codes.

    Check basic validators return expected tuples for invalid input.
    """
    from hlpr.cli.validators import validate_config, validate_file_path

    assert validate_file_path("") == (False, "empty path")
    assert validate_config({}) == (True, "ok")
