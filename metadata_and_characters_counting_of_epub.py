from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from pathlib import Path


def get_epub_metadata(file_path):
    """
    Extract significant metadata from an EPUB document.
    Returns a dictionary with metadata details like title, author, publisher, and language.
    """
    book = epub.read_epub(file_path)
    metadata = {
        'title': book.get_metadata('DC', 'title'),
        'author': book.get_metadata('DC', 'creator'),
        'publisher': book.get_metadata('DC', 'publisher'),
        'language': book.get_metadata('DC', 'language'),
        'date': book.get_metadata('DC', 'date'),
    }
    return {key: value[0][0] if value else None for key, value in metadata.items()}


def count_epub_characters(file_path):
    """
    Count the total number of characters in the content of an EPUB document.
    Returns an integer with the character count.
    """
    book = epub.read_epub(file_path, options={'ignore_ncx': False})
    total_chars = 0

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text()
            total_chars += len(text)

    return total_chars


def print_info_of_2_epubs(filepath1, filepath2):
    file1_metadata = get_epub_metadata(filepath1)
    file1_count_chars = count_epub_characters(filepath2)

    file2_metadata = get_epub_metadata(filepath1)
    file2_count_chars = count_epub_characters(filepath2)

    print(f"Metadata for {Path(filepath1).stem}: {file1_metadata}")
    print(f"Total characters in {Path(filepath1).stem}: {file1_count_chars}")
    print(f"Metadata for {Path(filepath2).stem}: {file2_metadata}")
    print(f"Total characters in {Path(filepath2).stem}: {file2_count_chars}")


print_info_of_2_epubs('./639.epub', './656.epub')
