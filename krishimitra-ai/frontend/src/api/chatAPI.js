// frontend/src/api/diseaseAPI.js

import axiosClient from "./axiosClient";

/**
 * Detect plant disease from an uploaded leaf image.
 *
 * @param {File} imageFile - Uploaded leaf image.
 * @param {string} cropType - Optional crop name.
 * @returns {Promise<Object>} Disease detection result.
 */
export const detectDisease = async (imageFile, cropType = "") => {
  if (!imageFile) {
    throw new Error("Please select a leaf image first.");
  }

  const formData = new FormData();

  formData.append("image", imageFile);

  if (cropType) {
    formData.append("crop_type", cropType);
  }

  try {
    const response = await axiosClient.post(
      "/disease-detect",
      formData
    );

    console.log("Disease detection API response:", response.data);

    return response.data;
  } catch (error) {
    console.error(
      "Disease detection failed:",
      error.response?.data || error.message
    );

    throw new Error(
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Failed to detect plant disease."
    );
  }
};