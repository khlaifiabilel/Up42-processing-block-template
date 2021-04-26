import os

from geojson import FeatureCollection, Feature
from pathlib import Path
import rasterio as rio
import numpy as np

from blockutils.blocks import ProcessingBlock
from blockutils.datapath import (
    get_data_path,
    set_data_path,
    get_output_filename_and_path,
    get_in_out_feature_names_and_paths
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
        """Applies formula to uint16 image and outputs a uint8 array
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
        """
        Iterate through folders containing tif files,
        apply convert array method,
        Write && save converted 8bit arrays as new files.
        """


        if not input_fc.features:
            raise UP42Error(SupportedErrors.NO_INPUT_ERROR)

        output_fc = FeatureCollection([])

        for in_feature in input_fc["features"]:
            logger.info(f"Processing {in_feature}...")
            (
                _,
                out_feature_name,
                input_img_path,
                output_img_path,
            ) = get_in_out_feature_names_and_paths(in_feature, postfix="converted")

            with rio.open(input_img_path) as src:
                meta = src.meta
                arr = src.read()
                converted = self.convert_array(arr, np.uint8)
                meta['dtype'] = np.uint8

                with rio.open(output_img_path, 'w', **meta) as dst_dataset:
                    dst_dataset.write(converted)

            # Part of code to make the block work on up42
            out_feat = Feature(bbox=in_feature.bbox, geometry=in_feature.geometry)
            out_feat["properties"] = self.get_metadata(in_feature)
            out_feat = set_data_path(
                out_feat, out_feature_name
            )  # add new key, set relative path for the next plock
            logger.info(f"Processed {out_feat}...")
            output_fc.features.append(out_feat)

        return output_fc
