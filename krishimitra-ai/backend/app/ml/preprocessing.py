# backend/app/ml/preprocessing.py

import hashlib
import io
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_TARGET_SIZE = (224, 224)
DEFAULT_MAX_SIZE_MB = 5

ALLOWED_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
    "GIF",
    "BMP",
}


# ---------------------------------------------------------
# Image loading
# ---------------------------------------------------------

def _load_image(image_file) -> Image.Image:
    """
    Load an image from a file path, uploaded file,
    bytes object, or BytesIO object.

    Returns an RGB PIL image.
    """

    try:
        if isinstance(image_file, (str, Path)):
            image = Image.open(image_file)

        elif isinstance(image_file, (bytes, bytearray)):
            image = Image.open(io.BytesIO(image_file))

        elif hasattr(image_file, "read"):

            # Reset uploaded file pointer when possible.
            if hasattr(image_file, "seek"):
                image_file.seek(0)

            image = Image.open(image_file)

        else:
            raise ValueError(
                "Unsupported image input. "
                "Provide a file path, bytes, or uploaded file."
            )

        # Apply image orientation from EXIF metadata.
        image = ImageOps.exif_transpose(image)

        # Convert to RGB for the classification model.
        image = image.convert("RGB")

        # Force PIL to load the image data.
        image.load()

        return image

    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            f"Unable to read the uploaded image: {exc}"
        ) from exc

    except Exception as exc:
        if isinstance(exc, ValueError):
            raise

        raise ValueError(
            f"Image loading failed: {exc}"
        ) from exc


# ---------------------------------------------------------
# Image validation
# ---------------------------------------------------------

def validate_image(
    image_file,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
) -> bool:
    """
    Validate image size, format, and readability.

    Returns True when the image is valid.
    Raises ValueError when validation fails.
    """

    if image_file is None:
        raise ValueError("No image was provided.")

    # Check file size if available.
    file_size = None

    if hasattr(image_file, "size"):

        size_value = image_file.size

        if isinstance(size_value, int):
            file_size = size_value

    elif isinstance(image_file, (bytes, bytearray)):
        file_size = len(image_file)

    if (
        file_size is not None
        and file_size > max_size_mb * 1024 * 1024
    ):
        raise ValueError(
            f"Image is too large. Maximum size is "
            f"{max_size_mb} MB."
        )

    # Check extension when an uploaded filename exists.
    filename = getattr(image_file, "filename", None)

    if filename:
        extension = Path(filename).suffix.lower()

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
        }

        if extension not in allowed_extensions:
            raise ValueError(
                "Unsupported image extension. "
                "Use JPG, JPEG, PNG, WEBP, GIF, or BMP."
            )

    # Verify the image content.
    try:

        if isinstance(image_file, (str, Path)):

            with Image.open(image_file) as image:
                image_format = image.format
                image.verify()

        elif isinstance(image_file, (bytes, bytearray)):

            with Image.open(
                io.BytesIO(image_file)
            ) as image:
                image_format = image.format
                image.verify()

        else:

            if hasattr(image_file, "seek"):
                image_file.seek(0)

            with Image.open(image_file) as image:
                image_format = image.format
                image.verify()

            if hasattr(image_file, "seek"):
                image_file.seek(0)

        if image_format not in ALLOWED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {image_format}"
            )

        logger.info(
            "Image validation successful. Format: %s",
            image_format
        )

        return True

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            f"Invalid image file: {exc}"
        ) from exc

    finally:
        # Restore the pointer for subsequent processing.
        if hasattr(image_file, "seek"):
            try:
                image_file.seek(0)
            except Exception:
                pass


# ---------------------------------------------------------
# Main preprocessing function
# ---------------------------------------------------------

def preprocess_image(
    image_file,
    target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE,
    normalize: bool = True
) -> np.ndarray:
    """
    Preprocess a leaf image for TensorFlow/Keras inference.

    Args:
        image_file:
            Image path, bytes, or uploaded file.

        target_size:
            (width, height), default (224, 224).

        normalize:
            If True, divide RGB pixel values by 255.

    Returns:
        Float32 NumPy array with shape:

        (1, height, width, 3)

    Important:
        This preprocessing must match the training pipeline.
    """

    try:

        # Validate target dimensions.
        if (
            len(target_size) != 2
            or target_size[0] <= 0
            or target_size[1] <= 0
        ):
            raise ValueError(
                "target_size must contain positive "
                "width and height values."
            )

        # Load the image.
        image = _load_image(image_file)

        # PIL expects (width, height).
        image = image.resize(
            target_size,
            Image.Resampling.LANCZOS
        )

        # Convert RGB pixels to float32.
        image_array = np.asarray(
            image,
            dtype=np.float32
        )

        # Normalize only when requested.
        if normalize:
            image_array /= 255.0

        # Add the batch dimension.
        image_array = np.expand_dims(
            image_array,
            axis=0
        )

        # Ensure the output is valid.
        if not np.all(np.isfinite(image_array)):
            raise ValueError(
                "Preprocessed image contains invalid values."
            )

        logger.info(
            "Image preprocessed. Shape: %s, "
            "Range: [%.4f, %.4f]",
            image_array.shape,
            float(image_array.min()),
            float(image_array.max())
        )

        return image_array

    except Exception as exc:

        logger.exception(
            "Image preprocessing failed."
        )

        raise ValueError(
            f"Error preprocessing image: {exc}"
        ) from exc


# ---------------------------------------------------------
# Normalize an existing image array
# ---------------------------------------------------------

def normalize_image(
    image_array: np.ndarray
) -> np.ndarray:
    """
    Normalize image pixel values to [0, 1].

    Supports both individual images and batches.
    """

    image_array = np.asarray(
        image_array,
        dtype=np.float32
    )

    if image_array.size == 0:
        raise ValueError(
            "Cannot normalize an empty image array."
        )

    if not np.all(np.isfinite(image_array)):
        raise ValueError(
            "Image array contains invalid values."
        )

    if image_array.min() < 0:
        raise ValueError(
            "Image array contains negative pixel values."
        )

    if image_array.max() > 1.0:
        if image_array.max() > 255.0:
            raise ValueError(
                "Image pixel values exceed 255."
            )

        image_array = image_array / 255.0

    return image_array


# ---------------------------------------------------------
# Resize an image
# ---------------------------------------------------------

def resize_image(
    image,
    target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE
) -> Image.Image:
    """
    Resize a PIL image or NumPy image array.

    Returns a PIL RGB image.
    """

    if isinstance(image, np.ndarray):

        array = image

        # Remove a batch dimension if present.
        if array.ndim == 4 and array.shape[0] == 1:
            array = array[0]

        if array.ndim != 3:
            raise ValueError(
                "Expected an image array with "
                "height, width, and channels."
            )

        # Convert normalized values back to pixel values.
        if array.dtype != np.uint8:

            if array.max() <= 1.0 and array.min() >= 0:
                array = array * 255.0

            array = np.clip(
                array,
                0,
                255
            ).astype(np.uint8)

        image = Image.fromarray(array)

    if not isinstance(image, Image.Image):
        raise ValueError(
            "Expected a PIL image or NumPy array."
        )

    image = image.convert("RGB")

    return image.resize(
        target_size,
        Image.Resampling.LANCZOS
    )


# ---------------------------------------------------------
# Generate an image hash
# ---------------------------------------------------------

def get_image_hash(
    image_array: np.ndarray
) -> str:
    """
    Generate an SHA-256 hash of image-array contents.

    Identical arrays produce identical hashes.
    """

    image_array = np.ascontiguousarray(
        image_array
    )

    return hashlib.sha256(
        image_array.tobytes()
    ).hexdigest()


# ---------------------------------------------------------
# Extract image metadata
# ---------------------------------------------------------

def get_image_info(
    image_file
) -> dict:
    """
    Return image metadata for API responses.
    """

    try:

        file_size = None

        if hasattr(image_file, "size"):
            if isinstance(image_file.size, int):
                file_size = image_file.size

        elif isinstance(image_file, (bytes, bytearray)):
            file_size = len(image_file)

        image = _load_image(image_file)

        info = {
            "format": "unknown",
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "has_exif": bool(image.getexif()),
        }

        if file_size is not None:

            info["file_size_bytes"] = file_size

            info["file_size_kb"] = round(
                file_size / 1024,
                2
            )

        filename = getattr(
            image_file,
            "filename",
            None
        )

        if filename:
            info["filename"] = filename

        # Retrieve the original format where possible.
        try:

            if isinstance(image_file, (str, Path)):

                with Image.open(image_file) as original:
                    info["format"] = (
                        original.format or "unknown"
                    )

            elif isinstance(image_file, (bytes, bytearray)):

                with Image.open(
                    io.BytesIO(image_file)
                ) as original:
                    info["format"] = (
                        original.format or "unknown"
                    )

            else:

                if hasattr(image_file, "seek"):
                    image_file.seek(0)

                with Image.open(image_file) as original:
                    info["format"] = (
                        original.format or "unknown"
                    )

                if hasattr(image_file, "seek"):
                    image_file.seek(0)

        except Exception:
            pass

        logger.info(
            "Image information: %s",
            info
        )

        return info

    except Exception as exc:

        logger.exception(
            "Could not extract image metadata."
        )

        return {
            "error": str(exc),
            "format": "unknown",
            "size": (0, 0),
            "width": 0,
            "height": 0,
        }


# ---------------------------------------------------------
# Batch preprocessing
# ---------------------------------------------------------

def batch_preprocess(
    image_files: List,
    target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE,
    normalize: bool = True
) -> np.ndarray:
    """
    Preprocess multiple images into one batch.

    Returns an array shaped:

    (number_of_images, height, width, 3)
    """

    if not image_files:
        raise ValueError(
            "No images were provided."
        )

    processed_images = []

    for index, image_file in enumerate(image_files):

        try:

            processed = preprocess_image(
                image_file,
                target_size=target_size,
                normalize=normalize
            )

            processed_images.append(
                processed[0]
            )

        except Exception as exc:

            raise ValueError(
                f"Failed to preprocess image {index + 1}: "
                f"{exc}"
            ) from exc

    return np.stack(
        processed_images,
        axis=0
    )


# ---------------------------------------------------------
# ImagePreprocessor class
# ---------------------------------------------------------

class ImagePreprocessor:
    """
    Configurable image preprocessing utility.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE,
        normalize: bool = True
    ):

        self.target_size = target_size
        self.normalize = normalize

    def process(self, image_file) -> np.ndarray:

        return preprocess_image(
            image_file,
            target_size=self.target_size,
            normalize=self.normalize
        )

    def process_batch(
        self,
        image_files: List
    ) -> np.ndarray:

        return batch_preprocess(
            image_files,
            target_size=self.target_size,
            normalize=self.normalize
        )


# ---------------------------------------------------------
# Basic module test
# ---------------------------------------------------------

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    print("Testing image preprocessing...")

    # Create a sample image.
    sample_image = Image.new(
        "RGB",
        (300, 200),
        color=(40, 150, 60)
    )

    buffer = io.BytesIO()

    sample_image.save(
        buffer,
        format="JPEG"
    )

    image_bytes = buffer.getvalue()

    # Test preprocessing.
    processed = preprocess_image(
        image_bytes
    )

    print(
        "Processed shape:",
        processed.shape
    )

    print(
        "Processed dtype:",
        processed.dtype
    )

    print(
        "Pixel range:",
        float(processed.min()),
        float(processed.max())
    )

    print(
        "Image hash:",
        get_image_hash(processed)[:16]
    )

    print(
        "Image info:",
        get_image_info(image_bytes)
    )

    print("Preprocessing test completed.")