module.exports = function(app) {
  const fs = require("fs");
  const path = require("path");

  const LOG_PATH = path.join(__dirname, "../logs/ai_ping_log.json");

  app.get("/ai/ping", (req, res) => {
    const now = new Date().toISOString();

    let log = [];
    if (fs.existsSync(LOG_PATH)) {
      try {
        log = JSON.parse(fs.readFileSync(LOG_PATH, "utf8"));
      } catch (e) {
        log = [];
      }
    }

    log.push({ timestamp: now, ip: req.ip });

    fs.mkdirSync(path.join(__dirname, "../logs"), { recursive: true });

    fs.writeFileSync(LOG_PATH, JSON.stringify(log, null, 2));

    res.json({ ok: true, ts: now, total: log.length });
  });
};
