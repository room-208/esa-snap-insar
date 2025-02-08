import os
from logging import getLogger
from pathlib import Path
from typing import List

from esa_snappy import GPF, HashMap, Product, ProductIO

logger = getLogger(__name__)

OUTPUTS_DIR = Path(__file__).parent / "outputs"


def tops_sar_split(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("selectedPolarisations", "VV")
    parameters.put("subswath", "IW2")
    parameters.put("firstBurstIndex", "5")
    parameters.put("lastBurstIndex", "10")
    return GPF.createProduct("TOPSAR-Split", parameters, product)


def back_geocoding(primary_product: Product, secondary_product: Product) -> Product:
    parameters = HashMap()
    parameters.put("resamplingType", "BILINEAR_INTERPOLATION")
    parameters.put("outputRangeAzimuthOffset", "false")
    parameters.put("maskOutAreaWithoutElevation", "true")
    parameters.put("outputDerampDemodPhase", "false")
    parameters.put("disableReramp", "false")
    parameters.put("demName", "SRTM 3Sec")
    parameters.put("demResamplingMethod", "BILINEAR_INTERPOLATION")
    parameters.put("externalDEMNoDataValue", 0.0)
    return GPF.createProduct(
        "Back-Geocoding", parameters, [primary_product, secondary_product]
    )


def interferogram_formation(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("outputFlatEarthPhase", "false")
    parameters.put("subtractTopographicPhase", "false")
    parameters.put("cohWinAz", "3")
    parameters.put("includeCoherence", "true")
    parameters.put("srpPolynomialDegree", "5")
    parameters.put("srpNumberPoints", "501")
    parameters.put("cohWinRg", "10")
    parameters.put("outputElevation", "false")
    parameters.put("outputLatLon", "false")
    parameters.put("orbitDegree", "3")
    parameters.put("squarePixel", "true")
    parameters.put("subtractFlatEarthPhase", "true")
    parameters.put("tileExtensionPercent", "100")
    parameters.put("externalDEMApplyEGM", "true")
    parameters.put("outputTopoPhase", "false")
    parameters.put("demName", "SRTM 3Sec")
    parameters.put("externalDEMNoDataValue", 0.0)
    return GPF.createProduct("Interferogram", parameters, product)


def tops_deburst(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("selectedPolarisations", "VV")
    return GPF.createProduct("TOPSAR-Deburst", parameters, product)


def topophase_removal(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("orbitDegree", "3")
    parameters.put("outputElevationBand", "false")
    parameters.put("tileExtensionPercent", "100")
    parameters.put("outputLatLonBands", "false")
    parameters.put("outputTopoPhaseBand", "false")
    parameters.put("demName", "SRTM 3Sec")
    parameters.put("externalDEMNoDataValue", 0.0)
    return GPF.createProduct("TopoPhaseRemoval", parameters, product)


def goldstein_phase_filtering(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("alpha", "1.0")
    parameters.put("FFTSizeString", "64")
    parameters.put("useCoherenceMask", "false")
    parameters.put("coherenceThreshold", "0.2")
    parameters.put("windowSizeString", "3")
    return GPF.createProduct("GoldsteinPhaseFiltering", parameters, product)


def terrain_correction(product: Product) -> Product:
    parameters = HashMap()
    parameters.put("demName", "SRTM 3Sec")
    return GPF.createProduct("Terrain-Correction", parameters, product)


def save_product(product: Product) -> None:
    filepath = OUTPUTS_DIR / "insar.dim"
    ProductIO.writeProduct(product, filepath.resolve().as_posix(), "BEAM-DIMAP")


def main() -> None:
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    PRIMARY_SAR_PATH = os.getenv("PRIMARY_SAR_PATH")
    SECONDARY_SAR_PATH = os.getenv("SECONDARY_SAR_PATH")

    primary_product = ProductIO.readProduct(PRIMARY_SAR_PATH)
    secondary_product = ProductIO.readProduct(SECONDARY_SAR_PATH)

    primary_product = tops_sar_split(primary_product)
    secondary_product = tops_sar_split(secondary_product)

    insar_product = back_geocoding(primary_product, secondary_product)

    insar_product = interferogram_formation(insar_product)

    insar_product = tops_deburst(insar_product)

    insar_product = topophase_removal(insar_product)

    insar_product = terrain_correction(insar_product)

    save_product(insar_product)


if __name__ == "__main__":
    main()
