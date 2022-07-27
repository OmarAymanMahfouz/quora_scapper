from sqlalchemy import null, true
from config import *
from utilities import *

from time import sleep
import pymongo
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from urllib.parse import unquote

id
savedQuestions = set()

def WriteResult(question):
    myClient = pymongo.MongoClient("mongodb://localHost:20181")
    myDatabase = myClient['Quoras']
    myCollection = myDatabase['Articles']

    myCollection.insert_one(question)


def updateQuestionUrl(question):
    myClient = pymongo.MongoClient("mongodb://localHost:20181")
    myDatabase = myClient['Quoras']
    myCollection = myDatabase['Articles']

    myCollection.update_one({"Header": question['Header']}, {"$set": {"url": question['url'], "Body": question['Body']}})


def get_question_data(driver, questionUrl):
    js = {}

    driver.get(questionUrl)
    sleep(3)

    try:
        js['Header'] = driver.find_element(By.XPATH, "//div[@class='q-text qu-dynamicFontSize--xlarge qu-bold qu-color--gray_dark_dim qu-passColorToLinks qu-lineHeight--regular qu-wordBreak--break-word']").text
    except:
        js['Header'] = ""
        return
    
    js['Body'] = ""
    try:
        hidden_answers = driver.find_elements(By.XPATH, "//span[@class='q-text qu-cursor--pointer qt_read_more qu-color--blue_dark qu-fontFamily--sans qu-hover--textDecoration--underline']")

        for hidden in hidden_answers:
            hidden.click()
    except:
        pass

   # all_answers = "//div[@class='q-box dom_annotate_question_answer_item_0 qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised']"
    related_answers = "//div[@class='q-box dom_annotate_question_answer_item_0 qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised']//span[@class='q-box qu-userSelect--text']"
    answerindex = 0
    while True:
        try:
            #all_answers_elements =  driver.find_element(By.XPATH, all_answers)
            related_answers_elements = driver.find_elements(By.XPATH, related_answers)
        except:
            break

        # if 'ذات صلة' in all_answers_elements.text:
        #     break
        if len(related_answers_elements) > 1 or len(related_answers_elements) < 1:
            break
        js['Body'] += related_answers_elements[0].text + ' '
        related_answers = related_answers.replace(str(answerindex), str(answerindex + 1))
        answerindex += 1


    js['related-questions'] = set()
    
    try:
        related_questions = driver.find_elements(By.XPATH, "//div[@class='q-box dom_annotate_related_questions qu-borderAll qu-borderRadius--small qu-borderColor--raised qu-boxShadow--small qu-mb--small qu-bg--raised']//div[@class='q-box']//div//a")

        if len(related_questions) > 0:
            for i in related_questions:
                related = str(unquote(i.get_property('href')))
                js['related-questions'].add(related)
    except:
        pass

    return js


def checkQuoraUrl(quoraUrl):
    myClient = pymongo.MongoClient("mongodb://localHost:20181")
    myDatabase = myClient['Quoras']
    myCollection = myDatabase['Articles']

    x = myCollection.find_one({"url": quoraUrl})
    if x is None:
        return False
    
    return True

def get_saved_questions():
    global savedQuestions

    myClient = pymongo.MongoClient("mongodb://localHost:20181")
    myDatabase = myClient['Quoras']
    myCollection = myDatabase['Articles']

    documents = myCollection.find({"url": {"$exists" : False}})
    for document in documents:
        savedQuestions.add(document['Header'])


def get_questoins_count():
    myClient = pymongo.MongoClient("mongodb://localHost:20181")
    myDatabase = myClient['Quoras']
    myCollection = myDatabase['Articles']

    return myCollection.count_documents({})


def Scroller(driver):
    lastQuestionsCount = 0
    Noftries = 0

    while True:
        questionsCount = len(driver.find_elements(By.CSS_SELECTOR, 'a[class="q-box qu-display--block qu-cursor--pointer qu-hover--textDecoration--underline Link___StyledBox-t2xg9c-0 dxHfBI"]'))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)

        if lastQuestionsCount == questionsCount and NofScrollingTries == Noftries:
            break
        elif lastQuestionsCount == questionsCount:
            Noftries += 1
        else:
            Noftries = 0
        
        lastQuestionsCount = questionsCount


def get_questions_by_topic(driver, search_key_list):
    global id
    global savedQuestions

    #childDriver = init_driver(gecko_driver, user_agent=user_agent, is_headless=False)

    for key in search_key_list:
        url = quora_url + 'topic/' + key

        driver.get(url)
        sleep(5)
        

        Scroller(driver= driver)

        questions = []

        hreflist = driver.find_elements(By.CSS_SELECTOR, 'a[class="q-box qu-display--block qu-cursor--pointer qu-hover--textDecoration--underline Link___StyledBox-t2xg9c-0 dxHfBI"]')
        for href in hreflist:
            url = str(unquote(href.get_property('href')))
            if url not in questions:
                questions.append(url)

        for question in questions:
            try:
                if (checkQuoraUrl(question) == True):
                    continue
                
                data = get_question_data(driver, question)

                if len(data['Header']) == 0:   #An error occured durring page loading
                    continue


                js = {}
                js['Header'] = data['Header']
                js['Body'] = data['Body']
                js['ArticlID'] = id
                js['url'] = question

                if data['Header'] in savedQuestions:
                    updateQuestionUrl(js)
                else:
                    WriteResult(js)
                    id += 1
                
                for questionURL in data['related-questions']:
                    if questionURL not in questions:
                        questions.append(questionURL)
                
            except Exception as e:
                print(str(e))
                pass
    
    #childDriver.quit()


if __name__=="__main__":
    id = 200 * 1000 * 1000 + get_questoins_count()
    get_saved_questions()

    driver = init_driver(gecko_driver, user_agent=user_agent, is_headless=headless)
    
    # login to your account
    quora_login(driver= driver, username= quora_email, user_pwd=quora_password)

    search_key_list = [ 'لغة', 'الطب', 'التراث', 'الرياضيات', 'الكتابة', 'الاستثمار', 'البورصة', 'اقتصاديات', 'الاقتصاد', 'المالية', 
    'الأعمال', 'التقنية', 'الفن', 'السياسة', 'الأفلام', 'الطعام', 'الأدب', 'الفلسفة', 'الدراسة', 'البنوك', 'السياحة', 'الصحة', 'الرياضة', 
    'العلوم', 'الغناء', 'القراءة', 'الكتب', 'الهندسة','التسويق','الضرائب','الاطفال']
  

    get_questions_by_topic(driver, search_key_list)

    driver.quit()



# search_key_dic = [
#     {"search_key": f'لغة', "nofTweets": 10000},  {"search_key": f'الطب', "nofTweets": 10000},
#     {"search_key": f'التراث', "nofTweets": 500},  {"search_key": f'الرياضيات', "nofTweets": 500},
#     {"search_key": f'الكتابة', "nofTweets": 500},  {"search_key": f'الاستثمار', "nofTweets": 500},
#     {"search_key": f'البورصة', "nofTweets": 500},  {"search_key": f'اقتصاديات', "nofTweets": 500},
#     {"search_key": f'الاقتصاد', "nofTweets": 500},  {"search_key": f'المالية', "nofTweets": 500},
#     {"search_key": f'الأعمال', "nofTweets": 500},  {"search_key": f'التقنية', "nofTweets": 500},
#     {"search_key": f'السياسة', "nofTweets": 500},  {"search_key": f'الفن', "nofTweets": 500},
#     {"search_key": f'الأفلام', "nofTweets": 1000},  {"search_key": f'الطعام', "nofTweets": 1000},
#     {"search_key": f'الأدب', "nofTweets": 500},  {"search_key": f'الفلسفة', "nofTweets": 500},
#     {"search_key": f'الدراسة', "nofTweets": 500},  {"search_key": f'البنوك', "nofTweets": 500},
#     {"search_key": f'السياحة', "nofTweets": 500},  {"search_key": f'الصحة', "nofTweets": 500},
#     {"search_key": f'الرياضة', "nofTweets": 500},  {"search_key": f'العلوم', "nofTweets": 500},
#     {"search_key": f'الغناء', "nofTweets": 500},  {"search_key": f'الاطفال', "nofTweets": 500},
#     {"search_key": f'التسويق', "nofTweets": 500},  {"search_key": f'الضرائب', "nofTweets": 500},
#     {"search_key": f'الكتب', "nofTweets": 1000},  {"search_key": f'الهندسة', "nofTweets": 1000},
#     {"search_key": f'القراءة', "nofTweets": 500}
# ]