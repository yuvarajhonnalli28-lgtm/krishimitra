# backend/app/ml/predictor.py

import json
import logging
import os
import threading

from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
import tensorflow as tf

from .preprocessing import preprocess_image, validate_image


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Model paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "plant_disease_model"
    / "model.h5"
)

LABELS_PATH = (
    BASE_DIR
    / "models"
    / "plant_disease_model"
    / "labels.json"
)


# ---------------------------------------------------------
# Mock disease classes
# Only used when mock mode is explicitly enabled.
# These are NOT real model predictions.
# ---------------------------------------------------------

MOCK_DISEASES = [
    "Tomato Late Blight",
    "Tomato Early Blight",
    "Tomato Healthy",
    "Potato Late Blight",
    "Potato Early Blight",
    "Potato Healthy",
    "Rice Blast",
    "Rice Brown Spot",
    "Rice Healthy",
    "Wheat Yellow Rust",
    "Wheat Brown Rust",
    "Wheat Healthy",
    "Corn Northern Leaf Blight",
    "Corn Common Rust",
    "Corn Healthy",
]


# ---------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------

CONFIDENCE_THRESHOLDS = {
    "high": 0.85,
    "medium": 0.70,
    "low": 0.50,
}


# ---------------------------------------------------------
# Disease Predictor
# ---------------------------------------------------------

class DiseasePredictor:
    """
    Loads a trained plant disease model and predicts diseases
    from uploaded leaf images.

    Mock predictions are disabled by default.
    """

    def __init__(self, use_mock: bool = False):

        self.model = None
        self.labels = None

        self.use_mock = use_mock
        self.model_loaded = False
        self.load_error = None

        # Prevent simultaneous model initialization.
        self._prediction_lock = threading.Lock()

        if not self.use_mock:
            self._load_model()

    # -----------------------------------------------------
    # Load model and labels
    # -----------------------------------------------------

    def _load_model(self) -> bool:
        """
        Load the trained model and its class labels.
        """

        try:

            if not MODEL_PATH.is_file():

                self.load_error = (
                    f"Model file not found: {MODEL_PATH}"
                )

                logger.error(self.load_error)
                return False

            if not LABELS_PATH.is_file():

                self.load_error = (
                    f"Labels file not found: {LABELS_PATH}"
                )

                logger.error(self.load_error)
                return False

            logger.info(
                "Loading disease model from: %s",
                MODEL_PATH
            )

            # Compile is unnecessary for inference.
            self.model = tf.keras.models.load_model(
                str(MODEL_PATH),
                compile=False
            )

            with open(
                LABELS_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                self.labels = json.load(file)

            if not isinstance(self.labels, dict):

                raise ValueError(
                    "labels.json must contain a JSON object "
                    "mapping class indices to disease names."
                )

            # Normalize keys to strings.
            self.labels = {
                str(key): str(value)
                for key, value in self.labels.items()
            }

            # Check model output shape.
            output_shape = self.model.output_shape

            if isinstance(output_shape, list):

                raise ValueError(
                    "This predictor expects a single-output model."
                )

            num_classes = output_shape[-1]

            if num_classes is None:

                raise ValueError(
                    "Unable to determine the model output classes."
                )

            # Ensure every model output has a matching label.
            missing_labels = [
                str(index)
                for index in range(int(num_classes))
                if str(index) not in self.labels
            ]

            if missing_labels:

                raise ValueError(
                    "Missing class labels for output indices: "
                    + ", ".join(missing_labels)
                )

            if len(self.labels) != int(num_classes):

                raise ValueError(
                    f"Model outputs {num_classes} classes, "
                    f"but labels.json contains "
                    f"{len(self.labels)} labels."
                )

            self.model_loaded = True
            self.load_error = None

            logger.info(
                "Disease model loaded successfully."
            )

            logger.info(
                "Model input shape: %s",
                self.model.input_shape
            )

            logger.info(
                "Model output shape: %s",
                self.model.output_shape
            )

            logger.info(
                "Number of disease classes: %s",
                num_classes
            )

            logger.info(
                "Disease labels: %s",
                self.labels
            )

            return True

        except Exception as exc:

            self.model = None
            self.labels = None
            self.model_loaded = False

            self.load_error = str(exc)

            logger.exception(
                "Failed to load the disease model."
            )

            return False

    # -----------------------------------------------------
    # Predict disease
    # -----------------------------------------------------

    def predict(
        self,
        image_file,
        crop_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict a disease from an uploaded image.

        Returns a dictionary containing the prediction,
        confidence, alternatives, and model information.
        """

        try:

            if self.use_mock:

                return self._predict_mock(
                    image_file,
                    crop_type
                )

            # Never silently replace a missing model
            # with a random prediction.
            if not self.model_loaded or self.model is None:

                return {
                    "success": False,
                    "error": (
                        self.load_error
                        or "The trained disease model is not loaded."
                    ),
                    "disease": "Unknown",
                    "confidence": 0.0,
                    "severity": "uncertain",
                    "model_used": "none",
                    "message": (
                        "Please check the trained model and "
                        "labels.json files."
                    ),
                }

            # Validate the uploaded image.
            validate_image(image_file)

            # Process the image.
            logger.info(
                "Preprocessing uploaded leaf image."
            )

            image_tensor = preprocess_image(image_file)

            # Verify image dimensions against the model.
            expected_shape = self.model.input_shape

            if isinstance(expected_shape, list):

                raise ValueError(
                    "Multiple model inputs are not supported."
                )

            expected_height = expected_shape[1]
            expected_width = expected_shape[2]
            expected_channels = expected_shape[3]

            actual_shape = image_tensor.shape

            if (
                expected_height is not None
                and actual_shape[1] != expected_height
            ):

                raise ValueError(
                    f"Model expects image height "
                    f"{expected_height}, but received "
                    f"{actual_shape[1]}."
                )

            if (
                expected_width is not None
                and actual_shape[2] != expected_width
            ):

                raise ValueError(
                    f"Model expects image width "
                    f"{expected_width}, but received "
                    f"{actual_shape[2]}."
                )

            if (
                expected_channels is not None
                and actual_shape[3] != expected_channels
            ):

                raise ValueError(
                    "Image channels do not match model input."
                )

           # Make the actual prediction.
with self._prediction_lock:
    predictions = self.model.predict(
        image_tensor,
        verbose=0
    )

    print("\n========== DISEASE MODEL DEBUG ==========")
    print("Prediction scores:", predictions[0])
    print(
        "Predicted class index:",
        int(np.argmax(predictions[0]))
    )
    print(
        "Predicted confidence:",
        float(np.max(predictions[0]))
    )
    print("=========================================\n")

predictions = np.asarray(predictions)

            # This implementation expects a classifier
            # returning one score per class.
            if predictions.ndim != 2:

                raise ValueError(
                    "Unexpected prediction shape: "
                    f"{predictions.shape}"
                )

            if predictions.shape[0] != 1:

                raise ValueError(
                    "Expected exactly one prediction."
                )

            scores = predictions[0]

            if len(scores) != len(self.labels):

                raise ValueError(
                    "Prediction output count does not match "
                    "the number of class labels."
                )

            if not np.all(np.isfinite(scores)):

                raise ValueError(
                    "Model returned invalid prediction scores."
                )

            # Most classifiers return probabilities.
            # If the model returns logits, this normalization
            # makes scores comparable, but it does not replace
            # the need to verify the model's training setup.
            if (
                np.any(scores < 0)
                or np.any(scores > 1)
                or not np.isclose(
                    float(np.sum(scores)),
                    1.0,
                    atol=0.02
                )
            ):

                scores = tf.nn.softmax(
                    scores
                ).numpy()

            # Rank predictions from highest to lowest.
            top_indices = np.argsort(scores)[::-1][:3]

            primary_index = int(top_indices[0])

            disease_name = self.labels[
                str(primary_index)
            ]

            confidence = float(
                scores[primary_index]
            )

            severity = self._get_severity(
                confidence
            )

            # Return the next most likely predictions.
            alternatives = []

            for index in top_indices[1:]:

                index = int(index)

                alternatives.append({
                    "disease": self.labels[str(index)],
                    "confidence": round(
                        float(scores[index]),
                        4
                    ),
                })

            # Debug information helps diagnose repeated
            # predictions across different images.
            logger.info(
                "Predicted disease: %s",
                disease_name
            )

            logger.info(
                "Prediction confidence: %.4f",
                confidence
            )

            logger.info(
                "Top prediction scores: %s",
                [
                    {
                        "class_index": int(index),
                        "disease": self.labels[str(int(index))],
                        "score": round(
                            float(scores[int(index)]),
                            4
                        ),
                    }
                    for index in top_indices
                ]
            )

            return {
                "success": True,
                "disease": disease_name,
                "confidence": round(confidence, 4),
                "severity": severity,
                "alternatives": alternatives,
                "model_used": "trained",
                "crop_type": crop_type,
            }

        except Exception as exc:

            logger.exception(
                "Disease prediction failed."
            )

            return {
                "success": False,
                "error": str(exc),
                "disease": "Unknown",
                "confidence": 0.0,
                "severity": "uncertain",
                "model_used": "none",
                "message": (
                    "Prediction failed. Check the backend logs."
                ),
            }

    # -----------------------------------------------------
    # Mock prediction
    # -----------------------------------------------------

    def _predict_mock(
        self,
        image_file=None,
        crop_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Explicit development-only mock mode.

        These predictions are random and MUST NOT be used
        as real disease diagnoses.
        """

        import random

        available_diseases = MOCK_DISEASES

        if crop_type:

            filtered = [
                disease
                for disease in MOCK_DISEASES
                if disease.lower().startswith(
                    crop_type.lower()
                )
            ]

            if filtered:
                available_diseases = filtered

        disease = random.choice(
            available_diseases
        )

        confidence = random.uniform(
            0.65,
            0.98
        )

        alternatives = [
            {
                "disease": other,
                "confidence": round(
                    random.uniform(0.20, 0.60),
                    4
                ),
            }
            for other in available_diseases
            if other != disease
        ]

        random.shuffle(alternatives)

        logger.warning(
            "MOCK MODE ACTIVE: generated random disease "
            "prediction. This is not an actual diagnosis."
        )

        return {
            "success": True,
            "disease": disease,
            "confidence": round(confidence, 4),
            "severity": self._get_severity(confidence),
            "alternatives": alternatives[:2],
            "model_used": "mock",
            "crop_type": crop_type,
            "message": (
                "Development-only mock prediction. "
                "Not a real disease diagnosis."
            ),
        }

    # -----------------------------------------------------
    # Confidence-based severity
    # -----------------------------------------------------

    def _get_severity(
        self,
        confidence: float
    ) -> str:
        """
        Classify prediction confidence.

        Note: confidence is not the actual biological
        severity of a plant disease.
        """

        if confidence >= CONFIDENCE_THRESHOLDS["high"]:
            return "high"

        if confidence >= CONFIDENCE_THRESHOLDS["medium"]:
            return "moderate"

        if confidence >= CONFIDENCE_THRESHOLDS["low"]:
            return "low"

        return "uncertain"

    # -----------------------------------------------------
    # Batch prediction
    # -----------------------------------------------------

    def batch_predict(
        self,
        image_files: list
    ) -> List[Dict[str, Any]]:
        """
        Predict diseases for multiple images.
        """

        results = []

        for image_file in image_files:

            result = self.predict(
                image_file
            )

            results.append(result)

        return results

    # -----------------------------------------------------
    # Model information
    # -----------------------------------------------------

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return model loading and configuration information.
        """

        if self.model_loaded and self.model is not None:

            return {
                "loaded": True,
                "model_path": str(MODEL_PATH),
                "labels_path": str(LABELS_PATH),
                "input_shape": self.model.input_shape,
                "output_shape": self.model.output_shape,
                "num_classes": len(self.labels),
                "layers": len(self.model.layers),
                "model_used": "trained",
            }

        return {
            "loaded": False,
            "mode": "mock" if self.use_mock else "unavailable",
            "model_path": str(MODEL_PATH),
            "labels_path": str(LABELS_PATH),
            "error": self.load_error,
            "message": (
                "The trained model is unavailable. "
                "Check model files and backend logs."
            ),
        }


# ---------------------------------------------------------
# Shared predictor instance
# ---------------------------------------------------------

_predictor_instance = None

_predictor_lock = threading.Lock()


def get_predictor(
    use_mock: bool = False
) -> DiseasePredictor:
    """
    Get or create the shared predictor instance.
    """

    global _predictor_instance

    with _predictor_lock:

        if _predictor_instance is None:

            _predictor_instance = DiseasePredictor(
                use_mock=use_mock
            )

        elif (
            _predictor_instance.use_mock != use_mock
        ):

            logger.warning(
                "A predictor already exists with a different "
                "mode. Keeping the existing instance."
            )

        return _predictor_instance


# ---------------------------------------------------------
# Backward-compatible prediction function
# ---------------------------------------------------------

def predict_disease(
    image_file,
    use_mock: bool = False
) -> Dict[str, Any]:
    """
    Predict disease from an uploaded image.
    """

    predictor = get_predictor(
        use_mock=use_mock
    )

    return predictor.predict(
        image_file
    )


# ---------------------------------------------------------
# Batch prediction
# ---------------------------------------------------------

def predict_diseases_batch(
    image_files: list
) -> List[Dict[str, Any]]:
    """
    Predict diseases for multiple images.
    """

    predictor = get_predictor()

    return predictor.batch_predict(
        image_files
    )


# ---------------------------------------------------------
# Model status
# ---------------------------------------------------------

def get_model_status() -> Dict[str, Any]:
    """
    Return the current model status.
    """

    predictor = get_predictor()

    return predictor.get_model_info()