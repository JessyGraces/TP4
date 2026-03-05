"""
Parametrized tests for the Unicode encoding CLI tool.
Tests all encoding conversion combinations.
"""

import pytest
import tempfile
import os
import sys
import subprocess
from pathlib import Path
from encoder import VALID_ENCODINGS as ENCODINGS

TEST_CONTENT = "Hello, World!"


@pytest.fixture
def encoder_script():
    """Get the path to the encoder script"""
    script_path = Path(__file__).parent.parent / 'encoder' / 'encoder.py'
    if not script_path.exists():
        pytest.fail(f"encoder.py not found at {script_path}")
    return script_path


def run_encoder(script, *args):
    """Helper to run the encoder script"""
    cmd = [sys.executable, str(script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


@pytest.mark.parametrize("encoding", ENCODINGS)
def test_roundtrip(encoder_script, encoding):
    """Test converting from UTF-8 and back preserves content"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(TEST_CONTENT)
        input_path = f.name

    # Convert to encoding
    encoding_path = tempfile.mktemp(suffix='.txt')
    result1 = run_encoder(
        encoder_script, 'convert',
        input_path, encoding_path,
        '-f', 'utf-8',
        '-t', encoding
    )

    assert result1.returncode == 0, f"First conversion failed: {result1.stderr}"

    # Convert back
    final_path = tempfile.mktemp(suffix='.txt')
    result2 = run_encoder(
        encoder_script, 'convert',
        encoding_path, final_path,
        '-f', encoding,
        '-t', 'utf-8'
    )

    assert result2.returncode == 0, f"Second conversion failed: {result2.stderr}"

    # Verify final content matches original
    with open(final_path, 'r') as f:
        final_text = f.read()

    assert final_text.strip() == TEST_CONTENT.strip(), f"Roundtrip failed for {encoding}"

    for path in [input_path, encoding_path, final_path]:
        if os.path.exists(path):
            os.unlink(path)
