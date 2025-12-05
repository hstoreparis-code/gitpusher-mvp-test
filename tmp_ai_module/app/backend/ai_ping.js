const fs = require('fs');
const path = require('path');

module.exports = function(app) {
    app.get("/ai-ping", (req, res) => {
        const logPath = path.join(__dirname, "../logs/ai_ping_log.json");
        let logs = { pings: [] };

        if (fs.existsSync(logPath)) {
            logs = JSON.parse(fs.readFileSync(logPath, "utf8"));
        }

        logs.pings.push({
            timestamp: new Date().toISOString(),
            userAgent: req.headers["user-agent"] || "",
            ip: req.ip
        });

        fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
        res.json({ ok: true, message: "AI ping logged" });
    });
}
