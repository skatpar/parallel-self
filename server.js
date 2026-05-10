import express from "express";
import cors from "cors";
import Anthropic from "@anthropic-ai/sdk";
import "dotenv/config";

const app = express();
app.use(cors());
app.use(express.json());

if (!process.env.ANTHROPIC_API_KEY) {
  console.error("ANTHROPIC_API_KEY not set. Add it to .env");
}

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

app.post("/api/claude", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) return res.status(400).json({ error: "missing prompt" });

    const msg = await client.messages.create({
      model: "claude-sonnet-4-5",
      max_tokens: 1000,
      messages: [{ role: "user", content: prompt }],
    });

    const text = msg.content
      .filter((b) => b.type === "text")
      .map((b) => b.text)
      .join("\n");

    res.json({ text });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Claude proxy on :${PORT}`));
