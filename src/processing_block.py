from geojson import FeatureCollection, Feature
from pathlib import Path
import rasterio as rio

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


class AProcessingBlock(ProcessingBlock):
    """
    A processing block template
    """

    def __init__(self, exponent: int = 2):
        super().__init__()
        self.exponent = exponent

    def process(self, input_fc: FeatureCollection) -> FeatureCollection:
        if not input_fc.features:
            raise UP42Error(SupportedErrors.NO_INPUT_ERROR)

        output_fc = FeatureCollection([])

        for feat in input_fc["features"]:
            logger.info(f"Processing {feat}...")
            input_path = Path("/tmp/input/") / Path(get_data_path(feat))
            with rio.open(input_path) as src:
                src_win = WindowsUtil(src)
                (output_name, output_path,) = get_output_filename_and_path(
                    input_path.name, postfix="processed"
                )
                dst_meta = src.meta.copy()
                with rio.open(output_path, "w", **dst_meta) as dst:
                    for win in src_win.windows_regular():
                        exp = src.read(window=win) ** self.exponent
                        dst.write(exp, window=win)

                out_feat = Feature(bbox=feat.bbox, geometry=feat.geometry)
                out_feat["properties"] = self.get_metadata(feat)
                out_feat = set_data_path(out_feat, output_name)
                logger.info(f"Processed {out_feat}...")
                output_fc.features.append(out_feat)

        return output_fc
