from geojson import FeatureCollection, Feature
from pathlib import Path
import rasterio as rio
import numpy as np

from blockutils.blocks import ProcessingBlock
from blockutils.datapath import (
    get_data_path,
    set_data_path,
    get_output_filename_and_path,
)
from blockutils.logging import get_logger
from blockutils.exceptions import UP42Error, SupportedErrors
from blockutils.windows import WindowsUtil

logger = get_logger(__name__)


class DtypeConversion(ProcessingBlock):
    # TODO: Update this description
    """
    A processing block template
    """

    @staticmethod
    def convert_array(in_array: np.ndarray) -> np.ndarray:
        """ Applies formula to uint16 image and outputs a uint8 array
            The solution is based on: https://stackoverflow.com/a/59193141
          Args:
              in_array (np.ndarray): input array
          Returns:
              np.ndarray: output array
        """

        arr_min = in_array.min()
        arr_max = in_array.max()
        target_type_max = 255
        target_type_min = 0
        target_type = np.uint8

        norm1 = (target_type_max - target_type_min) / (arr_max - arr_min)
        norm2 = target_type_max - norm1 * arr_max
        out_array = (norm1 * in_array + norm2).astype(target_type)
        return out_array

    def process(self, input_fc: FeatureCollection) -> FeatureCollection:
        if not input_fc.features:
            raise UP42Error(SupportedErrors.NO_INPUT_ERROR)

        output_fc = FeatureCollection([])

        for feat in input_fc["features"]:
            logger.info(f"Processing {feat}...")
            input_path = Path("/tmp/input/") / Path(get_data_path(feat))
            with rio.open(input_path) as src:

                (
                    output_name,
                    output_path,
                ) = get_output_filename_and_path(input_path.name, postfix="processed")
                dst_meta = src.meta.copy()
                with rio.open(output_path, "w", **dst_meta) as dst:
                    exp = src.read() + self.addition
                    dst.write(exp)

#Part of code to make the block work on up42
                out_feat = Feature(bbox=feat.bbox, geometry=feat.geometry)
                out_feat["properties"] = self.get_metadata(feat)
                out_feat = set_data_path(out_feat, output_name) #add new key, set relative path for the next plock
                logger.info(f"Processed {out_feat}...")
                output_fc.features.append(out_feat)

        return output_fc
