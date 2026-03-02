import os
import sys

# Test that we can import the modules
try:
    from modules.claude_client import create_client
    from modules.sitemap_analyzer import create_analyzer
    from modules.social_generator import create_generator
    print("✓ All modules imported successfully!")
    
    # Test Claude client initialization
    client = create_client()
    print("✓ Claude API client initialized!")
    
    # Test sitemap parsing
    analyzer = create_analyzer()
    with open('sitemap.xml', 'r', encoding='utf-8') as f:
        xml_content = f.read()
    urls = analyzer.parse_sitemap_content(xml_content)
    print(f"✓ Sitemap parsed: {len(urls)} URLs found")
    
    print("\n" + "="*60)
    print("SYSTEM READY!")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
