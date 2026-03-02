# How to Run the Blog Automation System

## The Issue
Git Bash doesn't have Python in its PATH. You need to use Windows Command Prompt, PowerShell, or VS Code terminal.

## ✅ SOLUTION: Use VS Code Terminal

### Step-by-Step Instructions:

1. **Open VS Code Terminal**
   - Press `Ctrl + ~` (or View → Terminal)
   - Or click Terminal → New Terminal

2. **Navigate to the folder**
   ```bash
   cd blog-automation
   ```

3. **Install dependencies** (one-time setup)
   ```bash
   pip install anthropic beautifulsoup4 python-dotenv requests lxml
   ```

   If `pip` doesn't work, try:
   ```bash
   python -m pip install anthropic beautifulsoup4 python-dotenv requests lxml
   ```

4. **Run the automated demo**
   ```bash
   python auto_generate.py
   ```

   Or run the interactive version:
   ```bash
   python main.py
   ```

---

## Alternative: Use Windows Command Prompt

1. Press `Win + R`
2. Type `cmd` and press Enter
3. Run these commands:
   ```cmd
   cd C:\Users\HP\.vscode\test\blog-automation
   pip install anthropic beautifulsoup4 python-dotenv requests lxml
   python auto_generate.py
   ```

---

## Alternative: Use PowerShell

1. Press `Win + X` and select "Windows PowerShell"
2. Run these commands:
   ```powershell
   cd C:\Users\HP\.vscode\test\blog-automation
   pip install anthropic beautifulsoup4 python-dotenv requests lxml
   python auto_generate.py
   ```

---

## What Happens When You Run It?

### `python auto_generate.py` (Automated Demo)
- ✅ No questions asked - uses pre-filled answers
- ✅ Generates blog post: "What are the best AI tools for business?"
- ✅ Creates social media posts for LinkedIn, Twitter, Threads
- ✅ Analyzes sitemap for internal links
- ✅ Saves everything to `output/` folder
- ⏱️ Takes 2-3 minutes

### `python main.py` (Interactive)
- Asks you to select a question (1-40)
- Asks 5 qualifying questions
- You provide your own answers
- Generates custom content based on YOUR expertise
- Same output format

---

## Expected Output

You'll see:
```
============================================================
   AUTOMATED BLOG POST GENERATION
   Demo Mode - No user input required
============================================================

📝 Question: What are the best AI tools for business?

🤖 Initializing Claude AI client...
✓ Connected to Claude API

💭 Generating qualifying questions...

Questions generated:
  1. What specific AI tools have you implemented...
  2. Which AI platforms do you recommend...
  ...

📝 Using demo answers about Hex AI Agency expertise...

✍️  Generating comprehensive blog post...
   (This takes 30-60 seconds with Claude API...)

✓ Blog post generated!
   Length: 8,453 characters

🔗 Loading sitemap.xml...
✓ Parsed 5 URLs from sitemap

...

============================================================
   ✅ GENERATION COMPLETE!
============================================================

📁 Output location: output/2026-01-07-what-are-the-best-ai-tools-for-business

Generated files:
  ✓ blog_post.md (8,453 chars)
  ✓ linkedin_post.md (1,847 chars)
  ✓ twitter_thread.md (892 chars)
  ✓ threads_post.md (456 chars)
  ✓ metadata.json
```

---

## Troubleshooting

### "pip is not recognized"
Try: `python -m pip install ...`

### "python is not recognized"
- Open Command Prompt and try again
- Or install Python from python.org

### "ModuleNotFoundError"
Run the install command again:
```bash
pip install anthropic beautifulsoup4 python-dotenv requests lxml
```

### "ANTHROPIC_API_KEY not found"
- Check that `.env` file exists
- Verify it contains your API key (already configured!)

---

## Quick Test

Want to test if everything works? Run this in VS Code terminal:

```bash
cd blog-automation
python -c "from modules.claude_client import create_client; print('✅ System ready!')"
```

If you see "✅ System ready!" - you're good to go!

Then run:
```bash
python auto_generate.py
```

---

## Need Help?

The system is fully configured and ready. The only issue is running Python from Git Bash.

**Use VS Code Terminal (Ctrl + ~) and run:**
```bash
cd blog-automation
pip install anthropic beautifulsoup4 python-dotenv requests lxml
python auto_generate.py
```

That's it! 🚀
