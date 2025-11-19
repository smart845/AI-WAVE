const https = require('https');

/**
 * Vercel Serverless Function
 * Прокси для публичных маркет-эндпоинтов Bybit:
 * /api/bybit/market/<path>?<query>
 * → https://api.bybit.com/v5/market/<path>?<query>
 */
module.exports = (req, res) => {
  const { path } = req.query || {};
  const tail = Array.isArray(path) ? path.join('/') : (path || '');

  // Собираем query без параметра path (он служебный)
  const { path: _omit, ...rest } = req.query || {};
  const searchParams = new URLSearchParams(rest);
  const queryString = searchParams.toString();

  const upstreamPath = `/v5/market/${tail}${queryString ? `?${queryString}` : ''}`;

  const options = {
    hostname: 'api.bybit.com',
    port: 443,
    path: upstreamPath,
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'Bybit-Sniper-Terminal/1.0'
    },
    timeout: 5000
  };

  const upstreamReq = https.request(options, (upstreamRes) => {
    let body = '';
    upstreamRes.on('data', (chunk) => (body += chunk));
    upstreamRes.on('end', () => {
      res.statusCode = upstreamRes.statusCode || 500;
      res.setHeader('Content-Type', 'application/json');
      try {
        // Прозрачно прокидываем JSON
        const parsed = JSON.parse(body);
        res.end(JSON.stringify(parsed));
      } catch (e) {
        // В случае не-JSON просто отдаём как есть
        res.end(body);
      }
    });
  });

  upstreamReq.on('error', (err) => {
    console.error('Bybit proxy error:', err.message);
    res.statusCode = 502;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      error: 'BYBIT_PROXY_ERROR',
      message: err.message,
    }));
  });

  upstreamReq.on('timeout', () => {
    upstreamReq.destroy();
    res.statusCode = 504;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      error: 'BYBIT_PROXY_TIMEOUT',
      message: 'Upstream Bybit API timeout',
    }));
  });

  upstreamReq.end();
};
