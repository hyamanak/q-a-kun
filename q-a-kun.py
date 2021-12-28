from bs4 import BeautifulSoup
import re


def get_title(soup, repo): ##get document title from tmx file
    title = soup.find_all("prop", type="project", limit=1)
    title_sentence = "<h1>QA Report of " + title[0].string + "</h1>"
    print(title_sentence, file=repo)

def prep_temp_html(html_file): ##makes base file from template
    for each_line in html_file:
        print(each_line, file=repo, end='')


def check_non_jp(target): ##check if there are any English in target
    non_jp_words = re.findall(r"[a-zA-Z]+", target)
    if len(non_jp_words) != 0:
       return non_jp_words
    else:
        return False

def check_words(source, target, non_jp_words): ##Check if there is wrong spelling in source, needs deduplicate
    no_match_list = []
    result = []
    #print(non_jp_words)
    for word in non_jp_words:
        if word not in source:
            no_match_list.append(word)
    if len(no_match_list) != 0:
        result = [source, target, no_match_list]
        return result
    else:
        return False
            
def write_to_report(check_list, repo):
    mis_word_list = []
    source, target, no_match_list = check_list    
    for mis_word in no_match_list:
        mis_word_list.append(mis_word)
    high_lighted_target = highlight(source, target, no_match_list, mis_word_list)
    mis_word_list_st = " ".join(mis_word_list)
    print("<p>" + "<strong>Unmatched Word(s):</strong> " + mis_word_list_st + "<br />" +
     "<strong>Source:</strong> " + source + "<br />" +
     "\n" + "<strong>Target:</strong>" + high_lighted_target + "</p>", file=repo)


def split_target_to_list(target):
    result = []
    eng_char = ""
    jp_char = ""
    counter = 0
    target_len = len(target) -1

    for char in target:
        if ord(char) <= 127 and ord(char) != 32:
            if len(jp_char):
                result.append(jp_char)
            eng_char += char
            jp_char = ""
            if is_last(counter, target_len):
                last_add(counter, target_len, eng_char, result)
            else:
                counter += 1 
        else:
            if len(eng_char):
                result.append(eng_char)
            if ord(char) != 32:
               jp_char += char
            eng_char = ""
            if is_last(counter, target_len):
                last_add(counter, target_len, jp_char, result)
            else:
                counter += 1

    return result

def last_add(counter, target_len, char_list, result):
    result.append(char_list)
   

def is_last(counter, target_len):
    return counter == target_len

def highlight(source, target, no_match_list, mis_word_st):
    target_list = split_target_to_list(target)##needs to be indivisual 'Red' 'Hat' 'Enterprise' and so on...
    copy_list = target_list
    for word in mis_word_st:
        copy_list[target_list.index(word)] = "<strong class=\"highlight\">" + word + "</strong>"
    highlighted_target = " ".join(copy_list)
        
    return highlighted_target
            
def message_on_template(repo):
    print("<p>There might be an error/errors.</p>" + 
    "\n" + "<p>The following word(s) is/are not in the source sentence.</p>", 
    file=repo)

with open("short.tmx", 'r') as fp, open("html_body.html", 'r') as temp, open("report.html", 'w+') as repo, open("html_body.html", 'r') as html_file:
    soup = BeautifulSoup(fp)
    prep_temp_html(temp)
    get_title(soup, repo)
    message_on_template(repo)

    check_dict = {} ##stores each source(key) and target(key) as a set 

    for id, line in enumerate(soup.find_all('seg')): ##separate each line with id and line
        if line.string != None: ## exludes None segments 
            if id % 2 == 0: 
            #print("\n")
            #print("Source: ", line.string)
                check_dict["source"] = line.string
            #print(check_dict)
            else:
            #print("Target: ", line.string)
                check_dict["target"] = line.string
            #print(check_dict)
        
            if 'source' in check_dict and 'target' in check_dict:
                check_non_jp_result = check_non_jp(check_dict['target'])
                if  check_non_jp_result:
                    check_word_result = check_words(check_dict['source'], check_dict['target'], check_non_jp_result)
                    if check_word_result:
                        write_to_report(check_word_result, repo)
            #print(check_dict )
                check_dict = {}

    print("</body>" + "\n" + "</html>", file=repo)
             
