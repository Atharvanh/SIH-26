import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
});

export const getForecast = async (state, commodity, market, days = 7) => {
  const response = await client.get('/forecast', {
    params: { state, commodity, market, days },
  });
  return response.data;
};

export const getSaleWindow = async (state, commodity, market, days = 7) => {
  const response = await client.get('/sale-window', {
    params: { state, commodity, market, days },
  });
  return response.data;
};

export const matchBuyers = async (commodity, quantity_quintals, quality_grade, farmer_lat, farmer_lon) => {
  const response = await client.post('/buyer-match', {
    commodity,
    quantity_quintals,
    quality_grade,
    farmer_lat,
    farmer_lon
  });
  return response.data;
};
