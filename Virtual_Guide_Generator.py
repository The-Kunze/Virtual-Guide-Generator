import argparse
import sys
import re
import requests
import csv
from pb_py import main as api

""""
This code will enable anyone to be able to instantaneously create and upload a virtual guide bot to their website by filling out
a simple txt or csv and providing their sdk credentials. 
"""

# a dictionary where each key is a question and each value is a list of the form:
# [terminal_reduction, [reductions]]

# generates a dict of reductions with the company name inserted where necsessary
def create_reductions_dict():
    reductions_file = open('reductions.txt','rb')
    q_dict = {}
    new_q = True
    question = ''
    term_reduction_next = False
    reduction_list = []
    for line in reductions_file:
        if line.strip() == 'END':
            break
        elif line.isspace():
            q_dict[question].append(reduction_list)
            new_q = True
        elif new_q:
            question = line.strip()
            q_dict[question] = []
            term_reduction_next = True
            reduction_list = []
            new_q = False
        elif term_reduction_next:
            term_reduction = line.strip()
            q_dict[question].append(line.strip())
            term_reduction_next = False
        else: 
            reduction_list.append(line.strip())
    return q_dict

def update_reductions_dict(reductions_dict,credentials_dict):
    if credentials_dict['short business name']:
        name = credentials_dict['short business name']
    elif credentials_dict['business name']:
        name = credentials_dict['business name']
    question_list = reductions_dict['What does your business or organization do?']
    reduction_list = question_list[1]
    for num in range(len(reduction_list)):
        reduction_list[num] =  reduction_list[num].replace('companyName', name)
    question_list[1] = reduction_list
    reductions_dict['What does your business or organization do?'] = question_list
    return reductions_dict

#this program will take a csv and interpret it for bot creation
def interpret_csv(path,qa_dict):
    ifile = open(path,'rb')
    reader = csv.reader(ifile)
    credentials_dict = {}
    questions = qa_dict.keys()
    for row in reader:
        question = row[0].strip()
        answer = row[1].strip()
        if answer:
            if question == 'User Key':
                credentials_dict['user_key'] = answer
            elif question == 'App ID':
                credentials_dict['app_id'] = answer
            elif question == 'Botname':
                pbots_botname = re.findall(r'[a-z0-9]+', answer.lower())[0]
                credentials_dict['name'] = answer
                credentials_dict['botname'] = pbots_botname
            elif question == 'Business Name':
                credentials_dict['business name'] = answer
            elif question == 'Short Business Name (if applicable)':
                credentials_dict['short business name'] = answer
            else:
                if question in questions:
                    qa_dict[question].append(answer)
    return credentials_dict, qa_dict    

#this program will take a txt file and interpret it for bot creation
def interpret_file(path,qa_dict):
    ifile = open(path, 'rb')
    credentials_dict = {}
    questions = qa_dict.keys()
    current_question = ''
    current_answer = ''
    for line in ifile:
        if not line.isspace():
            if line.startswith('User Key:'):
                credentials_dict['user_key'] = line.split(':')[1].strip()
            elif line.startswith('App ID:'):
                credentials_dict['app_id'] = line.split(':')[1].strip()
            elif line.startswith('Botname:'):
                name = line.split(':')[1].strip()
                pbots_botname = re.findall(r'[a-z0-9]+', name.lower())[0]
                credentials_dict['name'] = name
                credentials_dict['botname'] = pbots_botname
            elif line.startswith('Business Name:'):
                credentials_dict['business name'] = line.split(':')[1].strip()
            elif line.startswith('Short Business Name (if applicable):'):
                credentials_dict['short business name'] = line.split(':')[1].strip()
            else:
                stripped_line = line.strip() 
                if stripped_line in questions:
                    if current_answer and current_question:
                        qa_dict[current_question].append(current_answer)
                    current_question = stripped_line
                    current_answer = ''
                else:
                    if current_answer:
                        current_answer += ' ' + stripped_line
                    else:
                        current_answer += stripped_line
    if current_answer and current_question:
        qa_dict[current_question].append(current_answer)
    return credentials_dict, qa_dict    
                
    

#this program will generate the aiml files for the bot
def create_file(qa_dict):
    aiml_file = '<?xml version="1.0" encoding="UTF-8"?>\n<aiml>\n'
    aiml_file += '<!-- file: vguide.aiml -->\n'
    aiml_file += '<!-- this file was create using the Virtual Guide Generator provided by Pandorabots Inc. -->\n\n'
    aiml_file += '<category>\n<pattern>INIT CONVO</pattern>\n<template>\n<condition name="initGreeting">\n<li value="true"><srai>restart</srai></li>\n<li><srai>start</srai></li>\n</condition>\n</template>\n</category>\n\n\n<category>\n<pattern>START</pattern>\n<template>\n<random>\n<li>Hello! </li>\n<li>Hi there! </li>\n<li>Hiya! </li>\n<li>Howdy! </li>\n<li>Hi! </li>\n</random>\n<think><set name="initGreeting">true</set> <set name="helpGuide">false</set></think>I\'m <bot name="name"/>. <srai>initHelpOffer</srai></template>\n</category>\n\n\n<category>\n<pattern>RESTART</pattern>\n<template>\n<random>\n<li>You\'re back! </li>\n<li>Good to see you again! </li>\n<li>I was wondering if you\'d come back. </li>\n<li>It\'s you again! </li>\n</random>\n<srai>initHelpOffer</srai></template>\n</category>\n\n\n<category>\n<pattern>INITHELPOFFER</pattern>\n<template><think><set name="topic">helpOffered</set></think>\n<random>\n<li>Can I help you with anything?</li>\n<li>Would you like help with anything?</li>\n<li>Is there anything I can help you with?</li>\n<li>Is there something I can help you with?</li>\n</random>\n</template>\n</category>\n\n\n<category>\n<pattern>NO ^</pattern>\n<topic>helpOffered</topic>\n<template><think><set name="topic">*</set></think><srai>HelpTurnedDown</srai></template>\n</category>\n\n\n<category>\n<pattern>*</pattern>\n<topic>helpOffered</topic>\n<template><think><set name="topic">*</set></think><srai><star/></srai></template>\n</category>\n\n\n<category>\n<pattern>HELPTURNEDDOWN</pattern>\n<template>\n<random>\n<li>Okay! </li>\n<li>Alright! </li>\n<li>Sounds good! </li>\n</random>\n<srai>endchat</srai></template>\n</category>\n\n\n<category>\n<pattern>ENDCHAT</pattern>\n<template>\n<random>\n<li>Remember, if you have any more questions just click the pop-up window and I\'ll be here. </li>\n<li>If you change your mind just click the pop-up window. </li>\n<li>I\'ll be here in the pop-up if you need anything else. </li>\n<li>Just let me know if you need any more help. </li>\n</random>\n</template>\n</category>\n\n<category>\n<pattern>BYE</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>GOODBYE</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>SEE YOU LATER</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>TTYL</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>FAREWELL</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>BYE BYE</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>GOOD BYE</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>STOP</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>LEAVE ME ALONE</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>STOP TALKING</pattern>\n<template><srai>endlongchat</srai></template>\n</category>\n\n<category>\n<pattern>FAREWELLS</pattern>\n<template>\n<random>\n<li>Have a nice day!</li>\n<li>See ya!</li>\n<li>Bye for now!</li>\n<li>Thanks!</li>\n<li>Bye!</li>\n</random>\n</template>\n</category>\n\n<category>\n<pattern>ENDLONGCHAT</pattern>\n<template>\n<random>\n<li>It\'s been lovely chatting with you.</li>\n<li>Thanks for your time.</li>\n<li>It was fun talking to you.</li>\n<li>Thanks for stopping by.</li>\n<li>It\'s been a pleasure.</li>\n</random>\n<srai>farewells</srai></template>\n</category>\n\n\n\n<category>\n<pattern>HELPOFFER</pattern>\n<template><think><set name="topic">HelpOffer</set></think>\n<random>\n<li>What can I help you with?</li>\n<li>How can I help you?</li>\n<li>What can I help you with?</li>\n<li>What can I do for you?</li>\n</random>\n</template>\n</category>\n\n'
    aiml_file += make_cat('WHAT IS YOUR NAME','My name is <bot name="name"/>.', True)
    aiml_file += '\n'
    for key in qa_dict:
        value = qa_dict[key]
        terminal_reduction = value[0]
        reduction_set = value[1]
        if len(value) == 3:
            answer = value[2]
            for reduction in reduction_set:
                aiml_file += make_cat(reduction,terminal_reduction)
                aiml_file += '\n'
            aiml_file += make_cat(terminal_reduction,answer,True)
            aiml_file += '\n'
    aiml_file += '\n</aiml>'
    return aiml_file

#this program will receive a reduced pattern and a template representing a Q&A pair and generate the category which will be appended to the aiml files containing the reduction sets
def make_cat(pattern,template,terminal_pattern=False):
    new_cat = '<category>\n<pattern>' + pattern + '</pattern>\n<template>'
    if terminal_pattern:
        new_cat += template
    else:
        new_cat += '<srai>' + template + '</srai>'
    new_cat += '</template>\n</category>\n'
    return new_cat


#this program will create the bot and upload it to the server
def api_handler(credentials_dict, aiml_file, update):
    user_key = credentials_dict['user_key']
    app_id = credentials_dict['app_id']
    botname = credentials_dict['botname']
    host = 'aiaas.pandorabots.com'
    if not update:
        result = api.create_bot(user_key,app_id,host,botname)
        if result != botname + ' has been created!':
            return result
    #make sure to change demobots to aiaas when testing complete
    url = 'https://' + host + '/bot/' + app_id + '/' + botname + '/file/vguide.aiml'
    query = {"user_key": user_key}
    response =  requests.put(url, params=query, data=aiml_file)
    if not response.ok:
        return "There was a problem with uploading your aiml file"
    properties = '[["name","' + credentials_dict['name'] + '"],["default-get", "unknown"], ["default-property", "unknown"], ["default-map", "unknown"], ["learn-filename", "pops_learn.aiml"]]'
    url = 'https://' + host + '/bot/' + app_id + '/' + botname + '/properties'
    response = requests.put(url, params=query, data=properties)
    if not response.ok:
        return "There was a problem with uploading your aiml file"
    result = api.compile_bot(user_key,app_id,host,botname)
    if result != botname + ' has been successfully compiled!':
        return result
    if update:
        result = credentials_dict['name'] + ' was updated successfully!'
    else:
        result = credentials_dict['name'] + ' was created and uploaded to ' + host + ' as ' + botname
    return result
        
    

#this program will be the main generator, orchestrating the order of operations of the other programs above
def main(ifile,update=False):
    #make sure the botname works according to pbotz code
    q_dict = create_reductions_dict()
    if ifile.endswith('.csv'):
        credentials_dict,qa_dict = interpret_csv(ifile,q_dict)
    else:
        credentials_dict,qa_dict = interpret_file(ifile,q_dict)
    if len(credentials_dict) != 6:
        return 'There was an issue with your credentials. Please check them and retry'
    if not credentials_dict['business name']:
        return 'Please provide a name for your business or organization following "Business name: " in Q&A template.'
    reductions_dict = update_reductions_dict(qa_dict, credentials_dict)
    aiml_file = create_file(reductions_dict)
    result = api_handler(credentials_dict, aiml_file, update)
    return result


#this program will handle the commmand line interface
def Main(argv=None):
  parser = argparse.ArgumentParser(
    description='this generator takes a file consisting of credentials and question and answer pairs and creates a bot which is automatically uploaded to the pandorabots aiaas server')
  parser.add_argument('--input-file',
                      help='a .txt or .csv file of credentials and Q&A pairs',
                      metavar='ID', required=True)
  parser.add_argument('--update',
                      help='If bot has been created and needs only to be updated set to true.',
                      metavar='ID', required=False)
  args = parser.parse_args(argv[1:])
  if args.update:
      result = main(args.input_file,args.update)
  else:
      result = main(args.input_file)
  print result
      

if __name__ == "__main__":
  sys.exit(Main(sys.argv)) 
