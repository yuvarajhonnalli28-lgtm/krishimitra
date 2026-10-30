// weather api
import axiosClient from "./axiosClient"

export const getMarketPrices = async () => {
  const response = await axiosClient.get("/market-prices")
  return response.data
}