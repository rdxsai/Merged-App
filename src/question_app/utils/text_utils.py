"""
Text utility functions for the Canvas Quiz Manager.

This module contains functions for cleaning and processing text content,
including HTML cleaning, text normalization, and feedback processing.
"""

import re
from typing import List
from bs4 import BeautifulSoup, Comment, CData
import html

"""
Text utility functions for the Canvas Quiz Manager.

This module contains functions for cleaning and processing text content,
including HTML cleaning, text normalization, and feedback processing.
"""


# In your text_utils.py file

from bs4 import BeautifulSoup, Comment, CData
import html
# ... (other imports)

# In your text_utils.py file


#Helper functions to help identify table structure - 

def is_table_complex(table_tag) -> bool:
    if table_tag.find(lambda tag: tag.has_attr('rowspan') or tag.has_attr('colspan')):
        return True
    if table_tag.find(['caption', 'colgroup', 'tfoot']):
        return True
    if table_tag.find('table'):
        return True
    if table_tag.find(['td', 'th'], recursive=True).find(['p', 'div', 'ul', 'ol', 'h1', 'h2', 'h3']):
        return True
    if table_tag.find('th', scope='row') or table_tag.find(headers=True):
        return True
    if len(table_tag.select('thead > tr')) > 1:
        return True
    return False


def convert_simple_table_to_markdown(table_tag) -> str:
    """
    Converts a simple HTML table (a BeautifulSoup tag) to a Markdown table string.
    Assumes the table has been pre-validated as "simple".
    """
    markdown_lines = []
    
    # Process header
    header_row = table_tag.select_one('thead > tr')
    if not header_row:
        # Fallback for tables with no thead but a first row of th
        header_row = table_tag.select_one('tr:first-child')
        if not header_row or not header_row.find('th'):
            return table_tag.prettify() # Cannot convert, return as is

    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    markdown_lines.append(f"| {' | '.join(headers)} |")
    
    # Process separator
    separator = ['---'] * len(headers)
    markdown_lines.append(f"| {' | '.join(separator)} |")
    
    # Process body rows
    body_rows = table_tag.select('tbody > tr')
    if not body_rows:
        # Fallback for tables with no tbody
        body_rows = header_row.find_next_siblings('tr')

    for row in body_rows:
        cells = [td.get_text(strip=True).replace('\n', ' ') for td in row.find_all('td')]
        # Ensure row has same number of columns as header
        if len(cells) == len(headers):
            markdown_lines.append(f"| {' | '.join(cells)} |")

    return "\n".join(markdown_lines)

def clean_question_text(text: str) -> str:
    # ... (docstring) ...
    if text is None or not text.strip():
        return ""

    try:
        # PRE-PROCESSING STEP: Manually handle CDATA before parsing,
        # as lxml can sometimes discard it.
        text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)

        soup = BeautifulSoup(text, 'lxml')

        # 1. Initial Cleanup (same as before)
        for tag in soup(["script", "style", "link", "meta"]):
            tag.decompose()
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        # 2. Self-Contained Blocks (same as before)
        for pre in soup.find_all('pre'):
            language = ''
            code_tag = pre.find('code')
            if code_tag and code_tag.get('class'):
                lang_class = next((cls for cls in code_tag['class'] if cls.startswith('language-')), None)
                if lang_class:
                    language = lang_class.replace('language-', '')
            pre.replace_with(f"\n\n```__{language}\n{pre.get_text().strip()}\n```__\n\n")

        # 3. Table cleanup
        for table in soup.find_all('table'):
            if is_table_complex(table):
                table.replace_with(f"\n\n{table.prettify()}\n\n")
            else:
                markdown_table = convert_simple_table_to_markdown(table)
                table.replace_with(f"\n\n{markdown_table}\n\n")
                
    

        # 3. Specific Tags (same as before)
        for img in soup.find_all('img'):
            alt = img.get('alt', '')
            src = img.get('src', '')
            img.replace_with(f"![{alt}]({src})")
        for hr in soup.find_all('hr'):
            hr.replace_with('\n\n---\n\n')
        for br in soup.find_all('br'):
            br.replace_with('\n')

        # 4. Handle Lists (MODIFIED)
        for list_tag in reversed(soup.find_all(['ul', 'ol'])):
            # Add a single newline before the whole list block
            list_tag.insert_before('\n')
            indent_level = len(list(list_tag.find_parents(['ul', 'ol'])))
            indent = '  ' * indent_level

            for i, li in enumerate(list_tag.find_all('li', recursive=False)):
                prefix = f"{i + 1}." if list_tag.name == 'ol' else '-'
                # REMOVED the extra '\n' from here to prevent gappy lists
                li.insert(0, f"{indent}{prefix} ")
                li.unwrap()
            list_tag.unwrap()

        # 5. Block-level Tags (same as before)
        for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']):
            tag.insert_before('\n\n')
            tag.insert_after('\n\n')
            tag.unwrap()

        # 6. Inline Formatting (same as before, plus unwrap for span/a)
        # ... (strong, em, code handlers) ...
        for tag in soup.find_all(['strong', 'b']):
            tag.insert_before('**')
            tag.insert_after('**')
            tag.unwrap()
        for tag in soup.find_all(['em', 'i']):
            tag.insert_before('*')
            tag.insert_after('*')
            tag.unwrap()
        for tag in soup.find_all(['s', 'strike', 'del']):
            tag.insert_before('~~')
            tag.insert_after('~~')
            tag.unwrap()
        for tag in soup.find_all('code'):
            tag.insert_before('`')
            tag.insert_after('`')
            tag.unwrap()
        for tag in soup.find_all(['span', 'a']):
            tag.unwrap()

        # 7. Final Conversion and Cleanup (MODIFIED)
        result = soup.body.decode_contents() if soup.body else str(soup)
        result = html.unescape(result)
        result = result.replace("```__", "```")

        # More robust whitespace normalization
        result = re.sub(r'[ \t]+', ' ', result)
        result = re.sub(r' +\n', '\n', result)
        result = re.sub(r'\n[ \t]+', '\n', result) # Removes leading spaces on a new line
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip()

    except Exception as e:
        print(f"CRITICAL: Error processing HTML: {e}")
        return re.sub(r'<[^>]+>', '', text).strip()


def clean_html_for_vector_store(html_text: str) -> str:
    """Clean HTML tags and normalize text for vector store processing."""
    if not html_text:
        return ""

    soup = BeautifulSoup(html_text, "lxml")

    # Add a newline character after block-level elements to ensure separation
    for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'li']):
        tag.append('\n')

    # Get the text, which now includes our inserted newlines
    text = soup.get_text()

    # Normalize whitespace by splitting into lines, stripping each one,
    # and rejoining only the non-empty lines.
    lines = (line.strip() for line in text.splitlines())
    result = '\n'.join(line for line in lines if line)

    result = html.unescape(result)

    return result.strip()

# The other functions (clean_answer_feedback, get_all_existing_tags, etc.) remain unchanged.
# I'm omitting them here for brevity, but you should keep them in your file.

def clean_answer_feedback(feedback: str, answer_text: str = "") -> str:
    """
    Clean and format answer feedback text.

    This function processes feedback text to remove unwanted content and
    ensure it's properly formatted for display.

    Args:
        feedback (str): The feedback text to clean.
        answer_text (str): Optional answer text for context.

    Returns:
        str: The cleaned feedback text.

    Note:
        The function removes common unwanted patterns and normalizes whitespace.
    """
    if not feedback:
        return ""

    # Remove common unwanted patterns
    feedback = re.sub(r"Correct\.", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Incorrect\.", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Good job!", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Try again\.", "", feedback, flags=re.IGNORECASE)

    # Remove weight indicators
    feedback = re.sub(r"\(Weight:\s*\d+%?\)", "", feedback, flags=re.IGNORECASE)

    # Remove correctness indicators
    feedback = re.sub(r"\[✓\s*CORRECT\]", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"\[✗\s*INCORRECT\]", "", feedback, flags=re.IGNORECASE)

    # Remove answer text prefix if provided
    if answer_text and feedback.startswith(f"{answer_text}:"):
        feedback = feedback[len(f"{answer_text}:") :].strip()
    elif answer_text and feedback.startswith(f"{answer_text} "):
        feedback = feedback[len(f"{answer_text} ") :].strip()

    # Clean up whitespace but preserve newlines
    feedback = re.sub(
        r"[ \t]+", " ", feedback
    )  # Replace multiple spaces/tabs with single space
    feedback = re.sub(
        r"\n\s*\n", "\n\n", feedback
    )  # Normalize multiple newlines to double newlines
    feedback = feedback.strip()

    return feedback


def get_all_existing_tags(questions: List[dict]) -> List[str]:
    """
    Extract all unique tags from a list of questions.

    Args:
        questions (List[dict]): List of question dictionaries.

    Returns:
        List[str]: List of unique tags found in the questions.

    Note:
        Tags are extracted from the 'tags' field and split by commas.
    """
    tags = set()
    for question in questions:
        if "tags" in question and question["tags"]:
            question_tags = [tag.strip() for tag in question["tags"].split(",")]
            tags.update(question_tags)
    return sorted(list(tags))


def extract_topic_from_text(text: str) -> str:
    """
    Extract a topic from text content.

    Args:
        text (str): The text to extract topic from.

    Returns:
        str: The extracted topic or 'general' if no topic found.

    Note:
        This is a simple implementation that could be enhanced with NLP.
    """
    if not text:
        return "general"

    # Simple keyword-based topic extraction
    text_lower = text.lower()

    # Accessibility keywords
    accessibility_keywords = [
        "accessibility",
        "screen reader",
        "alt text",
        "wcag",
        "aria",
        "accessible",
        "disability",
        "assistive",
    ]
    if any(word in text_lower for word in accessibility_keywords):
        return "accessibility"

    # Navigation keywords
    navigation_keywords = ["navigation", "menu", "nav", "breadcrumb", "sitemap"]
    if any(word in text_lower for word in navigation_keywords):
        return "navigation"

    # Forms keywords
    forms_keywords = ["form", "input", "label", "field", "submit", "validation"]
    if any(word in text_lower for word in forms_keywords):
        return "forms"

    # Media keywords
    media_keywords = ["video", "audio", "image", "caption", "transcript", "media"]
    if any(word in text_lower for word in media_keywords):
        return "media"

    # Keyboard keywords
    keyboard_keywords = ["keyboard", "shortcut", "tab", "focus", "arrow"]
    if any(word in text_lower for word in keyboard_keywords):
        return "keyboard"

    # Content keywords
    content_keywords = [
        "content",
        "semantic",
        "html",
        "structure",
        "heading",
        "element",
    ]
    if any(word in text_lower for word in content_keywords):
        return "content"

    return "general"
