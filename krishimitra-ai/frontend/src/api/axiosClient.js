// axios client
import axios from "axios"

const axiosClient = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json"
  },
  timeout: 10000
})

export default axiosClient