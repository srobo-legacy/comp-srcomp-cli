
import subprocess
import os.path

def test_dummy_is_valid():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_compstate = os.path.join(test_dir, 'dummy')
    try:
        subprocess.check_output(['srcomp', 'validate', dummy_compstate], \
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        assert cpe.returncode == 0, cpe.output
