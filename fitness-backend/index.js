require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const NUTRITIONIX_APP_ID = process.env.NUTRITIONIX_APP_ID;
const NUTRITIONIX_API_KEY = process.env.NUTRITIONIX_API_KEY;

// Allow requests only from your frontend origin
const allowedOrigins = ["http://localhost:5500", "http://127.0.0.1:5500"];

app.use(cors({
  origin: function (origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
  }
}));


app.use(express.json());

app.get('/api/food/:barcode', async (req, res) => {
  const barcode = req.params.barcode;
  try {
    const response = await axios.get(
      `https://trackapi.nutritionix.com/v2/search/item?upc=${barcode}`,
      {
        headers: {
          'x-app-id': NUTRITIONIX_APP_ID,
          'x-app-key': NUTRITIONIX_API_KEY,
        },
      }
    );

    const foodData = response.data.foods[0];
    if (!foodData) {
      return res.status(404).json({ error: 'Food not found' });
    }

    res.json({
      name: foodData.food_name,
      brand: foodData.brand_name,
      calories: foodData.nf_calories,
      fat: foodData.nf_total_fat,
      carbs: foodData.nf_total_carbohydrate,
      protein: foodData.nf_protein,
      serving: `${foodData.serving_qty} ${foodData.serving_unit}`,
    });
  } catch (error) {
    console.error('Error:', error.response ? error.response.data : error.message);
    res.status(500).json({ error: 'Failed to fetch food data', details: error.message });
  }
});

app.post('/api/food/advisor', async (req, res) => {
  const { text } = req.body;
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }
  try {
    const response = await axios.post('http://localhost:5001/advisor', { text });
    res.json(response.data);
  } catch (error) {
    console.error('Advisor service error:', error.message);
    res.status(500).json({ error: 'Failed to process advisor request', details: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
