import express from 'express';
import cors from 'cors';
import fs from 'fs';
import { exec } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import path from 'path';
import os from 'os';

const app = express();
app.use(cors());
app.use(express.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// /api/run: executes JS code and compares output
app.post('/api/run', async (req, res) => {
  const { code, testCases } = req.body;

  const results = await Promise.all(testCases.map((testCase, index) => {
    return new Promise((resolve) => {
      const jsCode = `${code}\nconsole.log(${testCase.input});`;
      const tempFilePath = path.join(os.tmpdir(), `temp_code_${Date.now()}_${index}.js`);
      fs.writeFileSync(tempFilePath, jsCode);

      exec(`node "${tempFilePath}"`, (error, stdout, stderr) => {
        fs.unlinkSync(tempFilePath);
        const output = stdout.replace(/\s+/g, '').trim();
        const expected = testCase.expected.trim();
        const passed = output === expected;
        resolve({
          testCase: index + 1,
          status: passed ? "✅ Passed" : `❌ Failed - Expected ${expected} but got ${output}`
        });
      });
    });
  }));

  res.json({ results });
});

// /api/scrape: runs Python script to scrape title from URL
app.post('/api/scrape', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: "URL is required" });

  const scriptPath = path.join(__dirname, 'scraper.py');

  exec(`python "${scriptPath}" "${url}"`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: stderr || error.message });
    }
    res.json({ title: stdout.trim() });
  });
});

app.listen(8080, () => {
  console.log("🚀 Server running on http://localhost:8080");
});
