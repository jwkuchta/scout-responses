import csv
import json
import requests
import io

#find a way to automate retrieval
jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImJyYmF0dEBobnRiLmNvbSIsImV4cCI6MTYyODM0OTAzNCwiZW1haWwiOiJicmJhdHRAaG50Yi5jb20ifQ.W1G_zF6vy5kREVdjLQjRKL8y9yId2Ntd6f36VqQ_D2I"

survey_id = 3

survey_json_url = "https://staging-api.scoutfeedback.com/api/surveyJSON"
survey_resp_url = "https://staging-api.scoutfeedback.com/api/responseJSON"
stakeholders_url = "https://staging-api.scoutfeedback.com/api/stakeholders"

survey_json = requests.post(f"{survey_json_url}/{survey_id}", headers={"authorization": jwt})
survey_responses_json = requests.post(survey_resp_url, headers={"authorization": jwt})
stakeholders_json = requests.post(stakeholders_url, headers={"authorization": jwt})

# parsed response
survey = json.loads(survey_json.text)
survey_responses = json.loads(survey_responses_json.text)
stakeholders = json.loads(stakeholders_json.text)

survey_questions = [question for question in survey['survey_json']['pages'][0]['elements']]
survey_json = requests.post(f"{survey_json_url}/{survey_id}", headers={"authorization": jwt})
survey_responses = [r for r in survey_responses if r['survey'] == survey_id]

def create_questions_dict(survey_questions):
    questions = {}
    for question in survey_questions:
        questions[question['name']] = question.get('title', 'NOTITLE')
    return questions

header_title_dict = create_questions_dict(survey_questions)

headers = []
for response in survey_responses:
    response_list = [""] * len(headers) # create placeholders
    for answer in response['response_json']:
        headers.append(answer)

headers = list(set(headers)) + ["comment_location"] + ['stakeholder_id']

to_csv = []
to_csv.append([header_title_dict.get(header, 'NOTITLE') for header in headers])


count = 0
for response in survey_responses:
    count+=1
    print('response: ', response['response_json'], '\n')
    comment_location = response['comment_location']
    response_list = [""] * len(headers) # create placeholders
    response_list[headers.index('comment_location')] = comment_location
    for question, answer in response['response_json'].items():
        response_list[headers.index(question)] = answer
    to_csv.append(response_list)

print('RESPONSE COUNT: ', count, '\n')

with io.open('camp_resp_w3.csv', mode='w', newline="", encoding="utf-8") as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(to_csv)
