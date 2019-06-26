import requests
import urllib.parse as p
import bs4
import argparse
import textwrap
import re

CLEAR = "\033[0m"
QUESTION = "\033[95m"
CODE = "\033[42m\033[30m"
LINK = "\033[94m"
BOLD = "\033[1m"
CYAN = "\033[46m\033[30m"

is_url = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def code_to_string(soup):
    l = []
    for tag in soup:
        s = [c for c in str(tag.string)]
        if len(s) > 1:
            for i, c in enumerate(s[:-2]):
                if s[i + 1] == c and c == "\n":
                    s.pop(i)
        string = "".join(s)
        l.append(string)

    s = "".join(l)
    if "\n" in s:
        # multiline comment
        s = s.rstrip()
        v = s.split("\n")
        l = []
        for x in v:
            l.append(CODE + x.rstrip() + CLEAR)
        s = "\n".join(l)
    else:
        s = CODE + s + CLEAR
    s.replace("\n", "    \n")
    return s


def parse_p(tag):
    l = []
    contents = tag.contents
    contents
    for x in contents:
        if type(x) == str:
            l.append(x)
        else:
            if x.name == "a":
                if not re.match(is_url, x.text):
	                l.append(x.text + LINK + "[%s]" % x["href"] + CLEAR)
                else:
                        l.append(LINK + "%s" % x.text + CLEAR)
            elif x.name == "b":
                l.append(BOLD + x.text + CLEAR)
            elif x.name == "code":
                l.append(CODE + x.text + CLEAR)
            elif x.name == "strike":
                pass
            else:
                l.append(str(x.string))

    retval = "".join(l)
    return retval


def parse_so_text(block):
    l = []
    for tag in block:
        if tag.name == "p":
            # normal text
            l.append(wrap(parse_p(tag)))
        elif tag.name == "pre":
            # code
            l.append(code_to_string(tag.find("code")))
    return "\n".join(l)


def pretty_print_string(string):
    counter = 0
    l = [c for c in string]
    last_space = []
    for i, c in enumerate(l):
        if c == "\n":
            counter = 0
        if c == ' ':
            last_space.append(i)
            counter += 1
        else:
            if counter < 80:
                counter += 1
            else:
                if len(last_space) > 0:
                    last = last_space.pop()
                    l[last] = '\n'
                    counter = i - last
                else:
                    l.insert(i+1, '\n')
                    counter = 0
    return "".join(l)

def wrap(string):
    l = textwrap.wrap(string, 80)
    return '\n'.join(l)


def main():

    parser = argparse.ArgumentParser(
        prog="so-search", description="Search stackoverflow.com for a question."
    )
    parser.add_argument(
        "question", metavar="Question", type=str, help="question to be searched"
    )

    args = vars(parser.parse_args())
    search_string = args["question"]

    query_string = p.quote_plus(search_string)
    search_r = requests.get("https://stackoverflow.com/search?q=%s" % query_string)
    search_soup = bs4.BeautifulSoup(search_r.text, "html.parser")

    surrounding_div = search_soup.find_all("div", "question-summary search-result")[0]
    assert surrounding_div != None
    votes = surrounding_div.find("span").find("strong").text
    try:
        answers = (
            surrounding_div.find("div", "status answered-accepted").find("strong").text
        )
    except AttributeError:
        answers = None
    tag = search_soup.find_all("a", "question-hyperlink")[0]
    print(QUESTION + "QUESTION: " + CLEAR + tag["title"])

    question_url = p.urljoin(
        "https://stackoverflow.com/search?q=%s" % query_string, tag["href"]
    )
    print(LINK + "(%s)" % question_url + CLEAR)
    answer_r = requests.get(question_url)
    answer_soup = bs4.BeautifulSoup(answer_r.text, "html.parser")
    if not answers:
        answers = answer_soup.find("div", "subheader answers-subheader").find("h2")[
            "data-answercount"
        ]

    print("(%s Answers, %s Votes)\n" % (answers, votes))

    question_block = answer_soup.find("div", "question").find("div", "post-text")
    question_text = parse_so_text(question_block)

    try:
        answer_block = answer_soup.find_all("div", "answer accepted-answer")[0]
    except:
        try:
            answer_block = answer_soup.find_all("div", "answer")[0]
        except:
            print()
            print(question_text)
            print()
            print(CYAN + 'NO ANSWERS' + CLEAR)
            return
    answer_votes = answer_block.find("div", {"itemprop": "upvoteCount"})["data-value"]
    answer_text = parse_so_text(answer_block.find("div", "post-text"))

    print()
    print(question_text)
    print()
    print(CYAN + "ANSWER: %s UPVOTES" % answer_votes + CLEAR)
    print()
    print(answer_text)
    print()

if __name__ == "__main__":
    main()
