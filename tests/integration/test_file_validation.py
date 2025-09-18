

def test_file_validation_integration():
    """T011: Integration test for file validation behavior.

    Use validate_file_path to confirm expected output for invalid input.
    """
    from hlpr.cli.validators import validate_file_path

    assert validate_file_path("") == (False, "empty path")
