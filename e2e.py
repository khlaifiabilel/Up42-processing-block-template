"""
End-to-end test: Fetches data, creates output, stores it in /tmp and checks if output
is valid.
"""

from pathlib import Path
import os

import geojson

from blockutils.common import setup_test_directories


if __name__ == "__main__":
    TESTNAME = "e2e_a-processing-block"
    TEST_DIR = Path("/tmp") / TESTNAME
    INPUT_DIR = TEST_DIR / "input"
    OUTPUT_DIR = TEST_DIR / "output"
    setup_test_directories(TEST_DIR)

    os.system(
        "gsutil cp -r gs://floss-blocks-e2e-testing/e2e_sharpening/sentinel2_rgb/input/ %s"
        % TEST_DIR
    )

    RUN_CMD = (
        """docker run -v %s:/tmp \
                 -e 'UP42_TASK_PARAMETERS={"exponent": 3}' \
                  -it a-processing-block"""
        % TEST_DIR
    )

    os.system(RUN_CMD)

    # Print out bbox of one tile
    GEOJSON_PATH = OUTPUT_DIR / "data.json"

    with open(str(GEOJSON_PATH)) as f:
        FEATURE_COLLECTION = geojson.load(f)

    out_path = FEATURE_COLLECTION.features[0]["properties"]["up42.data_path"]
    print(out_path)

    print("e2e test successful")
