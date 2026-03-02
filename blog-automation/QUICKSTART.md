# Quick Start Guide

## ✅ Setup Complete!

Your blog automation system is ready to use. Here's what's been configured:

### 1. API Key Configured
- ✅ Anthropic API key added to `.env`
- ✅ Using Claude Sonnet 4.5 model

### 2. Sitemap Ready
- ✅ Your hexaaiagency.com sitemap saved to `sitemap.xml`
- ✅ Contains 5 URLs for internal linking:
  - Homepage
  - Blog
  - Case Studies (main + 2 specific cases)

### 3. Question Bank Loaded
- ✅ 40 pre-loaded AI business questions
- ✅ First question ready: "What are the best AI tools for business?"

## 🚀 Run Your First Blog Post

### Option 1: Using Windows Command Prompt
```cmd
cd blog-automation
python main.py
```

### Option 2: Using PowerShell
```powershell
cd blog-automation
python main.py
```

### Option 3: Using Git Bash
```bash
cd blog-automation
python.exe main.py
```

## 📝 Workflow

When you run the script, it will:

1. **Show 10 questions** - Select #11: "What are the best AI tools for business?"
2. **Ask 5 questions** - Claude generates context questions about your expertise
3. **You answer** - Share your experience with AI tools
4. **Blog generation** - Takes 30-60 seconds
5. **Sitemap options** - Choose option 1 to use the saved sitemap.xml
6. **Internal links** - Claude suggests 3 relevant links
7. **Social posts** - Auto-generates LinkedIn, Twitter, Threads content
8. **Save** - Everything saved to `output/YYYY-MM-DD-topic/`

## 📊 Expected Output

```
output/2026-01-07-what-are-the-best-ai-tools-for-business/
├── blog_post.md          # 1500-2000 word blog post
├── linkedin_post.md      # Professional LinkedIn post
├── twitter_thread.md     # 4-6 tweet thread
├── threads_post.md       # Casual Threads post
└── metadata.json         # Generation metadata
```

## 💡 Tips

1. **Answer questions thoroughly** - More detail = better content
2. **Use sitemap option 1** - Your sitemap is already loaded
3. **Review before publishing** - AI content should be edited for your voice
4. **Customize prompts** - Edit files in `templates/` to adjust tone

## 🔧 Install Dependencies (if needed)

If you get import errors:

```cmd
cd blog-automation
pip install -r requirements.txt
```

Or if `pip` isn't found:

```cmd
python -m pip install -r requirements.txt
```

## ❓ Need Help?

- Check [README.md](README.md) for detailed documentation
- Verify API key in `.env` file
- Make sure you're in the `blog-automation` directory when running

## 🎯 Next Steps

1. Run `python main.py`
2. Follow the interactive prompts
3. Generate your first blog post
4. Copy content to your CMS
5. Schedule social posts
6. Repeat for all 40 questions! 🚀

---

**Ready? Let's go!**

```cmd
cd blog-automation
python main.py
```
