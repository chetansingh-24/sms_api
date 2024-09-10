const axios = require('axios');

let data = JSON.stringify({
  "user_id": 1,
  "template_id": 2,
  "sender_id": "admindddede5u",
  "text": "This is a sample SMS draft for the user.",
  "sms_type": "SMS"
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://push-draft-to-db-bxoz.onrender.com/create_sms_draft',
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  },
  data : data
};

axios.request(config)
.then((response) => {
  console.log(JSON.stringify(response.data));
})
.catch((error) => {
  console.log(error);
});
