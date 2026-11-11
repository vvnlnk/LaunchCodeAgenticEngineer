// Work around node-fetch 2.x "Premature close" on Node 20's keep-alive global agent
const https = require('https');
https.globalAgent = new https.Agent({ keepAlive: false });
