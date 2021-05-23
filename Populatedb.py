import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Enronproject.settings')
import django
django.setup()
from application1.models import Employee,mail_address,mail

from django.utils.timezone import datetime, timedelta, make_aware, timezone
import xml.etree.ElementTree as ET
import re
import pandas as pd


print(os.getcwd())

def pop_employee_adressmail(path_data):
    tree = ET.parse(path_data + '/employes_enron.xml')
    root = tree.getroot()
    for child in root:
        employee_record= Employee()
        #employee_record.save()
        try:
            employee_record.category = child.attrib['category'].lower()
        except KeyError:
            employee_record.category = 'Employee'.lower()
        for subchild in child:#child:employer
            if subchild.tag == 'lastname':
                employee_record.last_name = subchild.text.lower()
            elif subchild.tag == 'firstname':
                employee_record.first_name = subchild.text.lower()
            
            elif subchild.tag == 'mailbox':
                employee_record.mail_box = subchild.text.lower()       
        employee_record.save()
        for subchild in child:        
            if subchild.tag == 'email':
                mail_address_record = mail_address()
                mail_address_record.employee= employee_record
                mail_address_record.address = subchild.attrib['address'].lower()
                try:
                    t=mail_address.objects.get(address=subchild.attrib['address'].lower())
                except django.core.exceptions.ObjectDoesNotExist:
                    mail_address_record.save()






##tables des emails

#parsing functions
def parse_header(doc):
    keys = ['Message-ID']+re.findall('\n([\w\-]+):', doc[:doc.find('\n\n')])
    keys = pd.Series(keys).drop_duplicates().tolist()

    values = []
    for a, k in enumerate(keys):
        k = k+':'
        try:
            values.append(doc[doc.find(k)+len(k):doc.find(keys[a+1])].strip())
        except:
            values.append(doc[doc.find(k)+len(k):doc.find('\n\n')].strip())
    
    d = dict(zip(keys+['Body'],values+[doc[doc.find('\n\n'):].strip()])) 
    
    d['previous_mail_date']=''
    

    if d['Subject'][0:3]=='Re:':
        d['isReply']=True
        
        previous_date_pattern=r'\d\d/\d\d/\d\d\d\d \d\d:\d\d'
        try:
            d['previous_mail_date']=re.findall(previous_date_pattern, d['Body'])[0]
        except:
            pass 

    if d['Subject'][0:3].lower()!='re:':
        d['isReply']=False






    if 'Cc' not in d.keys():
        d['Cc']=''
    if 'X-cc' not in d.keys(): 
        d['X-cc']=''
    if 'To' not in d.keys():
        d['To']='' 
    if 'X-To' not in d.keys():
        d['X-To']=''    

    d['recepients_adresses']=d['To']  
    if len(d['Cc'])>0:
        d['recepients_adresses']=d['recepients_adresses']+','+d['Cc']            
        
    d['recepients_names']=d['X-To']
    if len(d['X-cc'])>0:
        d['recepients_names']=d['recepients_names']+','+d['X-cc']       
    return d



def convert_date(input_date,previous_date):
    
    if not previous_date:
        input_date=input_date[5:-12]
        converted_date = datetime.strptime(input_date, '%d %b %Y %H:%M:%S')
        #converting the date in UTC format
        UTC = timezone(timedelta(hours = 0))
        converted_date = converted_date.astimezone(UTC)
        return converted_date
    if previous_date:
        converted_date = datetime.strptime(input_date, '%m/%d/%Y %H:%M')
        UTC = timezone(timedelta(hours = 0))
        converted_date = converted_date.astimezone(UTC)
        return converted_date

def Extract_names_adresses(s1,s2):#s2=X-to + X-cc
    adresses=re.findall('[a-zA-Z]+[a-zA-Z\.]+@[a-zA-Z]+\.[a-zA-Z]{2,3}',s1)
    full_names=re.findall('[a-zA-Z]+, [a-zA-Z]+',s2)
    if len(full_names)==len(adresses):
        names_adresses=[[name.split(',')[0].strip(),name.split(',')[1].strip(),adr] for name,adr in zip(full_names,adresses)]
        return names_adresses#list of lists [last_name,first_name,adresse_mail]
    else:
        full_names=re.sub('([A-Z] ){1}','',s2)
        full_names=full_names.split(',')
        full_names=[k.strip() for k in full_names]
        names_adresses=[[name.split(' ')[0].strip().lower(),name.split(' ')[1].strip().lower(),adr] for name,adr in zip(full_names,adresses)]
        return names_adresses



#maildir process
def maildir_names_adresses_extraction(path_data):
    for folder,sub_folder,files in os.walk(path_data):
        for file in files:
            file_path = os.path.join(folder,file)
            #print(file_path)
            with open(file_path,'r') as doc:
                try:
                    dic=parse_header(doc.read())
                    #print(dic['From'])        
                    s1=dic['recepients_adresses']
                    s2=dic['recepients_names']
                    list_name_adresses=Extract_names_adresses(s1,s2)
                    #print(list_name_adresses)
                    #injection
                    if len(list_name_adresses)>0:
                       for liste in list_name_adresses:
                        
                            try:
                                t=mail_address.objects.get(address=liste[2].lower())
                            except django.core.exceptions.ObjectDoesNotExist:
                                employee_record=Employee()
                                employee_record.last_name=liste[0].lower()
                                employee_record.first_name=liste[1].lower()
                                if 'enron.com' in liste[2].lower():
                                    employee_record.category='employee'
                                if 'enron.com' not in liste[2].lower():
                                    employee_record.category='not employee'
                                employee_record.mail_box=liste[0].lower()+'-'+liste[1].lower()[0]                         
                                employee_record.save()

    
                                mail_address_record = mail_address()
                                mail_address_record.employee= employee_record
                                mail_address_record.address=liste[2].lower()
                                mail_address_record.save()
                                
                except:pass 





############################
#print(convert_date('Date: Wed, 13 Dec 2000 18:41:00 -0800 (PST)'[11:-6],False)





#print(mail_address.objects.get(address='rbandekow@home.com').id)  
def Populate_mails(path_data):
    for folder,sub_folder,files in os.walk(path_data):
        for file in files:
            file_path = os.path.join(folder,file)
            print(file_path)
            #with open(file_path,'r') as doc:
                        #lecture d'un mail
            with open(file_path,'r') as file:
                try:
                    #extraction des informations
                    message=file.read()
                    header=parse_header(message)

                    mail_date=convert_date(header['Date'],False)
                    subject=header['Subject']
                    sender=header['From']
    
                    recipients_adr=re.findall('[a-zA-Z\.]+@[a-zA-Z]+.[a-zA-Z]{2,3}',header['recepients_adresses'])
                    recipients_name=header['recepients_names']
                    isReply=header['isReply']

                    #injection dans la base de donnée

                    for rec in recipients_adr:
                        mail_record=mail()
                        mail_record.mail_date= mail_date
                        mail_record.subject=subject
                        mail_record.sender_mail=mail_address.objects.get(address=sender)
                        mail_record.recipient_mail=mail_address.objects.get(address=rec)
                        mail_record.isReply=isReply
                        if header['previous_mail_date']!='':
                            d=convert_date(header['previous_mail_date'], True)
                            if mail_date>d:
                                mail_record.previous_mail_date=d
                        mail_record.save()
                except:pass        


#data path:
path_data='/home/issamubuntu/Downloads/DATA'



# Decomment to populate 2 first tables from xml file  
#pop_employee_adressmail(path_data)

#Decemment to complet populating 2(Employee,mail_address) first tables
#maildir_names_adresses_extraction(path_data)


#Decomment to populat third Table( mail)
Populate_mails(path_data)





## TEST
"""
file_path="/home/issamubuntu/Downloads/DATA/maildir/allen-p/all_documents/192."
with open(file_path,'r') as doc:
    try:
        dic=parse_header(doc.read())
                    #print(dic['From'])        
        s1=dic['recepients_adresses']
        s2=dic['recepients_names']
        list_name_adresses=Extract_names_adresses(s1,s2)
        print(list_name_adresses)
        #injection
        if len(list_name_adresses)>0:
            for liste in list_name_adresses:
                #print(list[0].lower())
                try:
                    t=mail_address.objects.get(address=liste[2].lower())
                except django.core.exceptions.ObjectDoesNotExist:
                                #print(list[2].lower())
                                #if '@' not in liste[0] and '@' not in liste[1]:
                    employee_record=Employee()
                    employee_record.last_name=liste[0].lower()
                    employee_record.first_name=liste[1].lower()
                    if 'enron.com' in liste[2]:
                        employee_record.category='employee'
                    if 'enron.com' not in liste[2]:
                        employee_record.category='not employee'
                    employee_record.mail_box=liste[0].lower()+'-'+liste[1].lower()[0]                         
                    #employee_record.save()

    
                    mail_address_record = mail_address()
                    mail_address_record.employee= employee_record
                    mail_address_record.address=liste[2].lower()
                    #mail_address_record.save()
                                
    except:pass 
"""