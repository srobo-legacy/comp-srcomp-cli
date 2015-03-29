
import os
import mock

from sr.comp.cli.yaml_round_trip import command

def get_info(file_path):
    mod = os.stat(file_path).st_mtime

    with open(file_path, 'r') as f:
        content = f.read()

    return mod, content

def test_dummy_schedule():
    # Assumes that the dummy schedule is already properly formatted
    test_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_schedule = os.path.join(test_dir, 'dummy', 'schedule.yaml')

    orig_mod, orig_content = get_info(dummy_schedule)

    mock_settings = mock.Mock(file_path=dummy_schedule)
    command(mock_settings)

    new_mod, new_content = get_info(dummy_schedule)

    assert new_mod != orig_mod, "Should have rewritten the file"
    assert new_content == orig_content, "Should not have changed file content"
