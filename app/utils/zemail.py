import requests
import json

def normalize_str(input):
    #function to convert all special chars to their escaped versions
    output = input
    return output

def send_ztemplate(ZEPTO_KEY, to_list, cc_list, template_id, merge_data):
    url = "https://api.zeptomail.com/v1.1/email/template"
    email_dict = {'from':{'address':''}}  #add this in the config/env file
    email_dict['template_key'] = template_id
    email_dict['bounce_address'] = ''  #add this in the config/env file
    clean_to_list = []
    for item in to_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_to_list.append(base_dict)
    #print(clean_to_list)
    email_dict['to'] = clean_to_list
    clean_cc_list = []
    for item in cc_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_cc_list.append(base_dict)
    #print(clean_cc_list)
    bcc_list = []  #add this in the config/env file
    clean_bcc_list = []
    for item in bcc_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_bcc_list.append(base_dict)
    #print(clean_bcc_list)
    email_dict['to'] = clean_to_list
    email_dict['cc'] = clean_cc_list
    email_dict['bcc'] = clean_bcc_list
    email_dict['merge_info'] = merge_data
    payload = json.dumps(email_dict)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"{ZEPTO_KEY}",
    }
    print(headers, payload)
    #return False
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return response

def send_zemail(ZEPTO_KEY, to_list, cc_list, subject, body):
    url = "https://api.zeptomail.com/v1.1/email"

    email_dict = {'from':{'address':''}} #add this in the config/env file

    clean_to_list = []
    for item in to_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_to_list.append(base_dict)
    print(clean_to_list)
    email_dict['to'] = clean_to_list

    clean_cc_list = []
    for item in cc_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_cc_list.append(base_dict)
    #print(clean_cc_list)
    email_dict['cc'] = clean_cc_list

    bcc_list = [] #add this in the config/env file
    clean_bcc_list = []
    for item in bcc_list:
        base_dict = {"email_address":{}}
        base_dict.get("email_address")["address"] = item
        clean_bcc_list.append(base_dict)
    #print(clean_bcc_list)
    email_dict['bcc'] = clean_bcc_list

    clean_subject = normalize_str(subject)
    email_dict['subject'] = clean_subject

    clean_body = normalize_str(body)
    email_dict['htmlbody'] = clean_body

    payload = json.dumps(email_dict)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"{ZEPTO_KEY}",
    }

    print(headers, payload)
    #return False
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return response
