import pytest
from blockutils.exceptions import UP42Error
from context import AProcessingBlock


def test_a_processing_block():
    with pytest.raises(SystemExit) as excinfo:
        a_processing_block = AProcessingBlock()
        a_processing_block.run()
    # Makes sures empty input returns exit code 3 (NO_INPUT_ERROR)
    assert excinfo.value.code == 3
