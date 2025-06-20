import express from "express";
import cors from "cors";
import { spawn } from "child_process";
import fs from "fs";

const app = express();
const PORT = 8080;

// ✅ Load JSON manually
const slugsByDifficulty = JSON.parse(
  fs.readFileSync("./slugs_by_difficulty.json", "utf-8")
);

app.use(cors());
app.use(express.json());

app.post("/api/scrape", async (req, res) => {
  const { difficulty } = req.body;

  if (!difficulty || !slugsByDifficulty[difficulty]) {
    return res.status(400).json({ error: "Invalid or missing difficulty" });
  }

  const slugList = slugsByDifficulty[difficulty];
  const randomSlug = slugList[Math.floor(Math.random() * slugList.length)];

  console.log(`📌 Scraping slug: ${randomSlug} (${difficulty})`);

  const python = spawn("python", ["scraper.py", randomSlug]);

  let dataString = "";
  python.stdout.on("data", (data) => {
    dataString += data.toString();
  });

  python.stderr.on("data", (err) => {
    console.error("❌ Python Error:", err.toString());
  });

  python.on("close", () => {
    try {
      const parsed = JSON.parse(dataString);
      res.json(parsed);
    } catch (e) {
      console.error("❌ JSON parse error:", e);
      res.status(500).json({ error: "Failed to parse Python response" });
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
