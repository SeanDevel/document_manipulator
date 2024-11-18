from ebooklib import epub
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re

'''
Data Structure of epub.toc

[
    ( {Section object}, [ {Link object}, {Link object}, ... {Link object} ] ),
    ( {Section object}, [ {Link object}, {Link object}, ... {Link object} ] ),
    ...
    ( {Section object}, [ {Link object}, {Link object}, ... {Link object} ] ),
]
'''

class Article:
    def __init__(self, title, vice_title, date, content):
        self.title = title
        self.vice_title = vice_title
        self.date = self.convert_date(date)
        self.content = content

    def convert_date(self, text_date: str):
        # Clean up the date string (remove ordinal suffixes)
        clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', text_date)

        # Convert the cleaned string to a datetime object
        date_obj = datetime.strptime(clean_date, "%B %d %Y")

        # Convert the datetime object to the desired format
        formatted_date = date_obj.strftime("%Y-%m-%d")
        return formatted_date

    def write_to_file(self):
        articles_dir = Path('./articles')
        if not articles_dir.exists():
            articles_dir.mkdir()
        filename = self.date+"_"+self.title+'.txt'
        with open(articles_dir.joinpath(filename), 'w', encoding='utf-8') as f:
            f.write(self.content)


class The_Economists_EPUB:
    def __init__(self, file_path):
        self.file_path = file_path
        # if set 'ignore_ncx' to True, you can't get the href of a section
        self.epub = epub.read_epub(file_path, options={'ignore_ncx': False})
        self.filename = Path(file_path).stem
        self.toc = self.epub.toc
        self.section_list = self.get_sections()

    def get_sections(self):
        section_list = []
        for section_or_link in self.toc:
            for item in section_or_link:
                if isinstance(item, epub.Section):
                    section_list.append((item.title, item.href))
        return section_list

    def get_links_by_section_number(self, section_number):
        link_list = []
        section = self.toc[section_number]
        links = section[1]
        for link in links:
            link_list.append((link.title, link.href))
        return link_list

    def write_sections_to_file(self):
        with open(f'toc_{self.filename}.txt', 'w', encoding='utf-8') as f:
            for toc in self.section_list:
                for title, href in toc:
                    f.write(f"{title}: {href}\n")

    def write_article_to_file_by_href(self, href):

        item = self.epub.get_item_with_href(href)

        soup = BeautifulSoup(item.content, 'html.parser')

        for tag in soup.find_all(['small']):
            tag.unwrap()

        # , class_=['te_fly_span', 'te_section_title']
        for elem in soup.find_all(['aside', 'figure']):
            elem.decompose()  # Removes the element from the tree

        text_parts = ["[English Reading Comprehension]\n"]

        title_main = soup.find('h1', class_='te_article_title').get_text()
        title_vice = soup.find('h3', class_='te_article_rubric').get_text()
        date_published = soup.find(
            'h3', class_='te_article_datePublished').get_text()

        # Extract content between <h3 class="te_article_datePublished"> and <span class="span_ufinish">
        start_tag = soup.find('h3', class_='te_article_datePublished')
        end_tag = soup.find('span', class_='span_ufinish')

        content = []
        # Extract content between the specified tags
        if start_tag and end_tag:
            for sibling in start_tag.find_all_next():
                if sibling == end_tag:
                    break
                content.append(str(sibling))

        text_parts.append(title_main+"\n\n")
        text_parts.append(title_vice+"\n\n")
        for elem in BeautifulSoup(''.join(content).strip(), 'html.parser').descendants:
            if elem.name == 'p':
                # Collect text within <p> tags
                text_parts.append(elem.get_text()+"\n\n")

        text = ''.join(text_parts).strip()

        article = Article(title_main, title_vice, date_published, text)
        try:
            article.write_to_file()
            print("Article written to file")
        except:
            print("Error writing to file")


if __name__ == "__main__":
    import sys
    epub_path = input('Enter the path of the EPUB file: ')
    my_epub = The_Economists_EPUB(epub_path)

    sections = my_epub.section_list

    def print_sections(sections):
        for i, section in enumerate(sections):
            print(f"{i+1}: {section[0]}")

    if sections:
        print("Sections:")
        print_sections(sections)
    else:
        print("No sections found.")
        sys.exit(1)

    while True:
        response = input('------\nPress "Q" for quit.\n' +
                         'Press "S" for listing sections.\n' +
                         'Input a number of section to show a list of articles of the section.\n')
        if response.lower() == 'q':
            sys.exit(0)
        elif response.lower() == 's':
            print("Sections:")
            print_sections(sections)
        elif re.match(r'^\d+$', response):
            if (int(response) > len(sections) or int(response) < 1):
                print("\n!!! Invalid section number !!!\n")
                continue
            section_index = int(response)-1
            articles = my_epub.get_links_by_section_number(section_index)
            for i, link in enumerate(articles):
                print(f"{i+1}: {link[0]}")
            article_number = input(
                'Enter the number of the article: \n(or a non-number to quit the level)\n')
            if re.match(r'^\d+$', article_number):
                if int(article_number) > len(articles) or int(article_number) < 1:
                    print("\n!!! Invalid article number. Back to previous level !!!\n")
                    continue
                article_number = int(article_number)-1
                article = articles[article_number]
                print("\nHere is the article you selected: \n" +
                      "******\n"+article[0]+"\n******\n")
                confirm_write = input(
                    'Do you want to write the article to file? (y/n): ')
                if confirm_write.lower() == 'y':
                    my_epub.write_article_to_file_by_href(
                        articles[article_number][1])
                else:
                    print("Article not written to file.")
                    continue
            else:
                print("\n-- Back to previous level --\n")
                print_sections(sections)
                continue
