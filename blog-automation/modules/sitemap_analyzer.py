"""
Sitemap Analyzer Module
Parses sitemap XML and extracts URLs for internal linking analysis
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class SitemapAnalyzer:
    """Handles sitemap parsing and URL extraction"""

    def __init__(self):
        self.urls = []

    def parse_sitemap_from_url(self, sitemap_url):
        """
        Fetch and parse sitemap from URL

        Args:
            sitemap_url: URL of the sitemap (e.g., https://example.com/sitemap.xml)

        Returns:
            List of URLs found in the sitemap
        """
        try:
            response = requests.get(sitemap_url, timeout=10)
            response.raise_for_status()
            return self.parse_sitemap_content(response.text)
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch sitemap from {sitemap_url}: {str(e)}")

    def parse_sitemap_content(self, xml_content):
        """
        Parse sitemap XML content

        Args:
            xml_content: Raw XML string of the sitemap

        Returns:
            List of URLs found in the sitemap
        """
        try:
            soup = BeautifulSoup(xml_content, 'xml')

            # Handle standard sitemap
            urls = [loc.text.strip() for loc in soup.find_all('loc')]

            # Handle sitemap index (if it contains other sitemaps)
            if not urls:
                sitemap_tags = soup.find_all('sitemap')
                if sitemap_tags:
                    # This is a sitemap index, would need to fetch child sitemaps
                    print("Note: This appears to be a sitemap index. Parsing first-level URLs only.")
                    urls = [loc.text.strip() for loc in soup.find_all('loc')]

            self.urls = urls
            return urls

        except Exception as e:
            raise Exception(f"Failed to parse sitemap XML: {str(e)}")

    def filter_urls_by_path(self, path_filter=None):
        """
        Filter URLs by path (e.g., only blog posts)

        Args:
            path_filter: String to filter URLs by (e.g., '/blog/')

        Returns:
            Filtered list of URLs
        """
        if not path_filter:
            return self.urls

        return [url for url in self.urls if path_filter in url]

    def get_url_summary(self):
        """
        Get summary statistics about the sitemap

        Returns:
            Dictionary with sitemap statistics
        """
        if not self.urls:
            return {"total_urls": 0}

        # Parse domains
        domains = set()
        paths = {}

        for url in self.urls:
            parsed = urlparse(url)
            domains.add(parsed.netloc)

            # Get first path segment
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                first_segment = '/' + path_parts[0]
                paths[first_segment] = paths.get(first_segment, 0) + 1

        return {
            "total_urls": len(self.urls),
            "domains": list(domains),
            "top_paths": dict(sorted(paths.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def format_urls_for_display(self, max_urls=50):
        """
        Format URLs for console display

        Args:
            max_urls: Maximum number of URLs to display

        Returns:
            Formatted string of URLs
        """
        if not self.urls:
            return "No URLs found"

        display_urls = self.urls[:max_urls]
        formatted = "\n".join([f"  - {url}" for url in display_urls])

        if len(self.urls) > max_urls:
            formatted += f"\n  ... and {len(self.urls) - max_urls} more URLs"

        return formatted


def create_analyzer():
    """Create and return a SitemapAnalyzer instance"""
    return SitemapAnalyzer()
