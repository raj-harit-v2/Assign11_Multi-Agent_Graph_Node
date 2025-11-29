from mcp.server.fastmcp import FastMCP, Context
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re
from pydantic import BaseModel, Field
from models import SearchInput, UrlInput
from models import PythonCodeOutput  # Import the models we need
import trafilatura  # For markdown conversion


@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    position: int
    markdown_content: Optional[str] = None  # Full markdown content from webpage


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


# Compiled regex patterns for ASCII normalization (compile once, reuse many times)
_RE_UNICODE_SPACES = re.compile(r'[\u00A0\u2000-\u200B\u202F\u205F\u3000]')
_RE_MULTI_SPACES = re.compile(r'[ \t]+')
_RE_ZERO_WIDTH = re.compile(r'[\u200B-\u200D\uFEFF]')
_RE_LINE_BREAKS = re.compile(r'\r\n|\r')
_RE_MULTI_NEWLINES = re.compile(r'\n{3,}')

def _normalize_ascii_spacing(text: str) -> str:
    """
    Normalize text to strict ASCII spacing between words.
    
    Removes non-breaking spaces and other special Unicode spacing characters,
    replacing them with standard ASCII spaces. Ensures proper spacing between words.
    
    Prompt Example: "Provide the summary using strict standard ASCII spacing 
    between all words. Do not use non-breaking spaces or any other special 
    character formatting."
    
    Args:
        text: Text string that may contain non-breaking spaces or special formatting
        
    Returns:
        Text string with strict ASCII spacing normalized
    """
    if not text:
        return text
    
    # Replace non-breaking spaces and other Unicode spacing characters with ASCII space
    # \u00A0 = non-breaking space
    # \u2000-\u200B = various Unicode spaces (en quad, em quad, thin space, etc.)
    # \u202F = narrow no-break space
    # \u205F = medium mathematical space
    # \u3000 = ideographic space
    text = _RE_UNICODE_SPACES.sub(' ', text)
    
    # Replace multiple consecutive spaces with single ASCII space
    text = _RE_MULTI_SPACES.sub(' ', text)
    
    # Remove zero-width characters that might cause concatenation issues
    # \u200B = zero-width space
    # \u200C = zero-width non-joiner
    # \u200D = zero-width joiner
    # \uFEFF = zero-width no-break space (BOM)
    text = _RE_ZERO_WIDTH.sub('', text)
    
    # Normalize line breaks to standard newlines
    text = _RE_LINE_BREAKS.sub('\n', text)
    
    # Clean up multiple consecutive newlines (but preserve markdown structure)
    # Keep at least one newline for paragraph breaks
    text = _RE_MULTI_NEWLINES.sub('\n\n', text)
    
    # Strip leading/trailing whitespace from each line (but preserve intentional indentation)
    lines = text.split('\n')
    normalized_lines = []
    for line in lines:
        # Preserve markdown list indentation and code block indentation
        if line.strip().startswith(('*', '-', '+', '#', '```', '    ', '\t')):
            # Keep original line for markdown formatting
            normalized_lines.append(line.rstrip())
        else:
            # Normalize regular text lines
            normalized_lines.append(line.strip())
    
    return '\n'.join(normalized_lines)


def _replace_images_with_captions(markdown: str) -> str:
    """
    Replace markdown image syntax with descriptive text.
    
    Converts images from `![alt text](url)` format to `**Image:** [alt text or description]`.
    This maintains context while removing binary image data for text-only processing.
    
    Args:
        markdown: Markdown string containing image references
        
    Returns:
        Markdown string with images replaced by descriptive text
    """
    def replace(match):
        alt_text = match.group(1).strip()
        image_url = match.group(2).strip()
        
        # Use alt text if available, otherwise use URL as description
        if alt_text:
            return f"**Image:** {alt_text}"
        else:
            # Extract filename or use URL as description
            filename = image_url.split("/")[-1].split("?")[0] if "/" in image_url else image_url
            return f"**Image:** [Image from: {filename}]"
    
    # Match markdown image syntax: ![alt text](url)
    return re.sub(r'!\[(.*?)\]\((.*?)\)', replace, markdown)


class DuckDuckGoSearcher:
    """
    DuckDuckGo HTML Text-Mode Searcher
    
    This class provides privacy-focused, text-mode search using DuckDuckGo's HTML interface.
    It is the default search engine for all information queries in the system.
    
    Benefits:
    - Privacy: No tracking, no cookies, no personalization
    - Speed: Text mode (HTML) is faster than JavaScript-heavy interfaces
    - Reliability: HTML parsing is more stable than dynamic content scraping
    - Consistency: Same interface for all queries ensures predictable results
    - Lower Bandwidth: Text-only responses use less data
    - Bot-Friendly: HTML interface is designed for programmatic access
    - No Rate Limiting Issues: Text mode is less likely to trigger anti-bot measures
    """
    # DuckDuckGo HTML text-mode interface (default for all queries)
    BASE_URL = "https://html.duckduckgo.com/html"
    
    # Text mode configuration
    TEXT_MODE_ONLY = True  # Force text-only mode (no JavaScript)
    FORCE_TEXT_MODE = True  # Explicitly request text mode
    
    # Headers optimized for text-mode HTML requests
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, force_text_mode: bool = True):
        """
        Initialize DuckDuckGo searcher with text-mode configuration.
        
        Args:
            force_text_mode: If True, explicitly request text-only mode (default: True)
        """
        self.rate_limiter = RateLimiter()
        self.force_text_mode = force_text_mode
        # Reuse HTTP client for connection pooling (performance optimization)
        self._client = None

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format results in a natural language style that's easier for LLMs to process"""
        if not results:
            return "No results were found for your search query. This could be due to DuckDuckGo's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."

        # Optimized: Use list comprehension + join for better performance
        output_lines = [f"Found {len(results)} search results:\n"]
        output_lines.extend(
            f"{result.position}. {result.title}\n   URL: {result.link}\n   Summary: {result.snippet}\n"
            for result in results
        )
        return "".join(output_lines)

    def format_results_with_markdown(self, results: List[SearchResult]) -> str:
        """
        Format search results including markdown content when available.
        
        Shows both snippet and full markdown content for results that have been
        fetched and converted to markdown format.
        
        Args:
            results: List of SearchResult objects, some may have markdown_content
            
        Returns:
            Formatted string with snippets and markdown content
        """
        if not results:
            return "No results were found for your search query. This could be due to DuckDuckGo's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."

        # Optimized: Use list comprehension + join for better performance
        output_lines = [f"Found {len(results)} search results:\n"]
        
        for result in results:
            output_lines.append(f"{result.position}. {result.title}\n   URL: {result.link}\n   Summary: {result.snippet}")
            
            # Add markdown content if available
            if result.markdown_content:
                output_lines.append("\n   Full Content (Markdown):\n   " + "=" * 60)
                # Indent markdown content for readability
                markdown_lines = result.markdown_content.split('\n')
                output_lines.extend("   " + line for line in markdown_lines[:100])  # Limit to first 100 lines
                if len(markdown_lines) > 100:
                    output_lines.append("   ... [markdown content truncated]")
                output_lines.append("   " + "=" * 60)
            
            output_lines.append("")  # Empty line between results

        return "\n".join(output_lines)

    async def search(
        self, query: str, ctx: Context, max_results: int = 10
    ) -> List[SearchResult]:
        """
        Search DuckDuckGo using HTML text-mode interface.
        
        POST data parameters:
        - "q": Search query (required)
        - "b": Browser identifier (empty = default text mode)
        - "kl": Language code (empty = auto-detect)
        - "kp": Safe search setting ("-1" = moderate, optional)
        - "ia": Instant answer ("off" = disable for text-only, optional)
        - "df": Date filter (optional)
        
        Args:
            query: Search query string
            ctx: MCP context for logging
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()

            # Create form data for POST request with explicit text mode parameters
            # The HTML interface is text-only by default, but we set explicit parameters
            # to ensure text mode and optimize for LLM processing
            data = {
                "q": query,  # Query string
                "b": "",     # Browser (empty = default text mode)
                "kl": "",    # Language (empty = auto-detect)
            }
            
            # Add optional text-mode parameters if force_text_mode is enabled
            if self.force_text_mode:
                # Disable instant answers for cleaner text-only results
                data["ia"] = "off"
                # Set safe search to moderate (optional, can be adjusted)
                data["kp"] = "-1"

            await ctx.info(f"Searching DuckDuckGo (text mode) for: {query}")

            # Reuse HTTP client for connection pooling (performance optimization)
            if self._client is None:
                self._client = httpx.AsyncClient(
                    headers=self.HEADERS,
                    timeout=30.0,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            
            result = await self._client.post(self.BASE_URL, data=data)
            result.raise_for_status()

            # Parse HTML result
            soup = BeautifulSoup(result.text, "html.parser")
            if not soup:
                await ctx.error("Failed to parse HTML result")
                return []

            results = []
            for result in soup.select(".result"):
                title_elem = result.select_one(".result__title")
                if not title_elem:
                    continue

                link_elem = title_elem.find("a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                link = link_elem.get("href", "")

                # Skip ad results
                if "y.js" in link:
                    continue

                # Clean up DuckDuckGo redirect URLs
                if link.startswith("//duckduckgo.com/l/?uddg="):
                    link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])

                snippet_elem = result.select_one(".result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                results.append(
                    SearchResult(
                        title=title,
                        link=link,
                        snippet=snippet,
                        position=len(results) + 1,
                    )
                )

                if len(results) >= max_results:
                    break

            await ctx.info(f"Successfully found {len(results)} results")
            return results

        except httpx.TimeoutException:
            await ctx.error("Search request timed out")
            return []
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            await ctx.error(f"Unexpected error during search: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return []

    async def search_with_markdown_content(
        self, 
        query: str, 
        ctx: Context, 
        max_results: int = 10,
        fetch_content: bool = True,
        max_content_results: int = 3
    ) -> List[SearchResult]:
        """
        Search DuckDuckGo and optionally fetch markdown content from top results.
        
        This method performs a regular search, then optionally fetches and converts
        the top N result URLs to markdown format for deeper content extraction.
        
        Args:
            query: Search query string
            ctx: MCP context for logging
            max_results: Maximum number of search results to return
            fetch_content: If True, fetch markdown content from top results (default: True)
            max_content_results: Maximum number of results to fetch markdown for (default: 3)
            
        Returns:
            List of SearchResult objects, with markdown_content populated for fetched results
        """
        try:
            # First, get regular search results
            results = await self.search(query, ctx, max_results)
            
            if not results or not fetch_content:
                return results
            
            # Fetch markdown content for top results
            fetcher = WebContentFetcher()
            fetched_count = 0
            
            for result in results[:max_content_results]:
                if fetched_count >= max_content_results:
                    break
                
                try:
                    await ctx.info(f"Fetching markdown content from: {result.link}")
                    markdown_content = await fetcher.fetch_and_convert_to_markdown(result.link, ctx)
                    
                    # Only store if we got valid content (not an error message)
                    if markdown_content and not markdown_content.startswith("Error:"):
                        result.markdown_content = markdown_content
                        fetched_count += 1
                    else:
                        await ctx.warn(f"Could not fetch markdown content from: {result.link}")
                except Exception as e:
                    await ctx.error(f"Error fetching markdown from {result.link}: {str(e)}")
                    # Continue with other results even if one fails
                    continue
            
            await ctx.info(f"Successfully fetched markdown content for {fetched_count} results")
            return results
            
        except Exception as e:
            await ctx.error(f"Unexpected error in search_with_markdown_content: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            # Fall back to regular search if markdown fetching fails
            return await self.search(query, ctx, max_results)


class WebContentFetcher:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=20)
        # Reuse HTTP client for connection pooling (performance optimization)
        self._client = None

    async def fetch_and_convert_to_markdown(self, url: str, ctx: Context) -> str:
        """
        Fetch webpage and convert to markdown format.
        
        Uses trafilatura to extract clean markdown content preserving structure
        (headings, lists, tables, links). Images are replaced with descriptive text.
        
        Args:
            url: URL of the webpage to fetch
            ctx: MCP context for logging
            
        Returns:
            Markdown string with clean content, or error message if failed
        """
        try:
            await self.rate_limiter.acquire()

            await ctx.info(f"Fetching and converting to markdown: {url}")

            # Use trafilatura to fetch and convert to markdown
            # trafilatura handles HTTP internally, but we could optimize further if needed
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                await ctx.error(f"Failed to download webpage: {url}")
                return f"Error: Failed to download the webpage from {url}"

            # Extract markdown content
            markdown = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                include_images=True,
                output_format='markdown'
            ) or ""

            if not markdown.strip():
                await ctx.warn(f"No content extracted from: {url}")
                return f"Error: No content could be extracted from {url}"

            # Normalize to strict ASCII spacing (remove non-breaking spaces, special formatting)
            # This ensures proper word spacing and removes concatenation issues
            markdown = _normalize_ascii_spacing(markdown)

            # Replace images with captions (text-only mode)
            markdown = _replace_images_with_captions(markdown)

            # Truncate if too long (keep structure by truncating at paragraph boundaries)
            if len(markdown) > 15000:
                # Try to truncate at a paragraph boundary
                truncated = markdown[:15000]
                last_para = truncated.rfind('\n\n')
                if last_para > 10000:  # Only truncate at paragraph if reasonable
                    markdown = truncated[:last_para] + "\n\n... [content truncated]"
                else:
                    markdown = truncated + "... [content truncated]"

            await ctx.info(
                f"Successfully converted to markdown ({len(markdown)} characters)"
            )
            return markdown

        except httpx.TimeoutException:
            await ctx.error(f"Request timed out for URL: {url}")
            return f"Error: The request timed out while trying to fetch {url}."
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            await ctx.error(f"Error converting {url} to markdown: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error: An unexpected error occurred while converting webpage to markdown ({str(e)})"

    async def fetch_and_parse(self, url: str, ctx: Context, use_markdown: bool = False) -> str:
        """
        Fetch and parse content from a webpage.
        
        Args:
            url: URL of the webpage to fetch
            ctx: MCP context for logging
            use_markdown: If True, returns markdown format; if False, returns plain text (default: False)
            
        Returns:
            Plain text or markdown string depending on use_markdown parameter
        """
        if use_markdown:
            return await self.fetch_and_convert_to_markdown(url, ctx)
        
        # Original plain text implementation (backward compatible)
        try:
            await self.rate_limiter.acquire()

            await ctx.info(f"Fetching content from: {url}")

            # Reuse HTTP client for connection pooling (performance optimization)
            if self._client is None:
                self._client = httpx.AsyncClient(
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    follow_redirects=True,
                    timeout=30.0,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                )
            
            result = await self._client.get(url)
            result.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(result.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Get the text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"

            await ctx.info(
                f"Successfully fetched and parsed content ({len(text)} characters)"
            )
            return text

        except httpx.TimeoutException:
            await ctx.error(f"Request timed out for URL: {url}")
            return "Error: The request timed out while trying to fetch the webpage."
        except httpx.HTTPError as e:
            await ctx.error(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            await ctx.error(f"Error fetching content from {url}: {str(e)}")
            return f"Error: An unexpected error occurred while fetching the webpage ({str(e)})"


# Initialize FastMCP server
mcp = FastMCP("ddg-search")
searcher = DuckDuckGoSearcher()
fetcher = WebContentFetcher()


@mcp.tool()
async def duckduckgo_search_results(input: SearchInput, ctx: Context) -> PythonCodeOutput:
    """
    Search DuckDuckGo in text mode (default search engine for all information queries).
    
    This is the default search tool for all information queries in the system.
    Uses DuckDuckGo's HTML text-mode interface for privacy-focused, fast, and reliable results.
    
    Args:
        input: SearchInput containing query and max_results
        ctx: MCP context for logging
        
    Returns:
        PythonCodeOutput with formatted search results
    """
    try:
        results = await searcher.search(input.query, ctx, input.max_results)
        return PythonCodeOutput(result=searcher.format_results_for_llm(results))
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"


@mcp.tool()
async def download_raw_html_from_url(input: UrlInput, ctx: Context) -> PythonCodeOutput:
    """Fetch webpage content. """
    return PythonCodeOutput(result=await fetcher.fetch_and_parse(input.url, ctx))


@mcp.tool()
async def duckduckgo_search_with_markdown(input: SearchInput, ctx: Context) -> PythonCodeOutput:
    """
    Search DuckDuckGo and fetch markdown content from top results.
    
    This enhanced search tool performs a DuckDuckGo search and then fetches
    and converts the top 3 result URLs to markdown format. This provides
    deeper content extraction with preserved structure (headings, lists, tables).
    Images are converted to descriptive text for text-only processing.
    
    Benefits:
    - Preserves document structure (better for LLM processing)
    - Token-efficient markdown format
    - Full content from top results (not just snippets)
    - Graphics handled as descriptive text
    
    Args:
        input: SearchInput containing query and max_results
        ctx: MCP context for logging
        
    Returns:
        PythonCodeOutput with formatted search results including markdown content
    """
    try:
        results = await searcher.search_with_markdown_content(
            input.query, 
            ctx, 
            max_results=input.max_results,
            fetch_content=True,
            max_content_results=3
        )
        return PythonCodeOutput(result=searcher.format_results_with_markdown(results))
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return PythonCodeOutput(result=f"An error occurred while searching with markdown: {str(e)}")


if __name__ == "__main__":
    print("mcp_server_3.py starting")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
        print("\nShutting down...")