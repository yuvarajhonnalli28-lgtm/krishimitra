// disease api
import axiosClient from "./axiosClient"

export const detectDisease = async (imageFile) => {

  const formData = new FormData()
  formData.append("image", imageFile)

  const response = await axiosClient.post("/disease-detect", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  })

  return response.data
}