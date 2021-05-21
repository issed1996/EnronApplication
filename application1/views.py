from django.db.models import query
from django.shortcuts import render
from django.http import HttpResponse
from .models import Employee,mail,mail_address
from django.utils.timezone import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.db.models.functions import TruncDate
from django.db.models import Count
# Create your views here.



def home(request):
    return render(request, 'home.html')



def dictfetchall(cursor): 
    desc = cursor.description 
    return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
    ]

def employees(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    lines = request.GET.get('lines')
    minimum_threshold=request.GET.get('minimum_threshold')
    maximum_threshold=request.GET.get('maximum_threshold')
    if not lines:
        lines=10
    if lines:
        pass

    if not start_date:
        start_date= datetime(1999, 1, 1)
    if lines:
        pass


    if not end_date:
        end_date= datetime(2001, 1, 1)
    if lines:
        pass
    
    req=request.GET.get('request')
    if not req:
        users=Employee.objects.raw(f'SELECT * FROM application1_employee LIMIT {lines}')
    if req=='communicating most internaly':

    
        sufix_enron='%@enron.com'       
        most_intern_query=f"""select TAB.id,TAB.first_name,TAB.last_name,TAB.category,count(*) occurences 
                            FROM (SELECT  application1_employee.*
                            FROM application1_employee,application1_mail, application1_mail_address
                            WHERE application1_mail_address.id=application1_mail.sender_mail_id
                            AND application1_employee.id= application1_mail_address.employee_id
                            AND application1_mail.recipient_mail_id IN (SELECT DISTINCT application1_mail.recipient_mail_id
                            FROM application1_mail,application1_mail_address
                            WHERE application1_mail_address.id=application1_mail.recipient_mail_id
                            AND application1_mail_address.address LIKE '{sufix_enron}'
                            AND application1_mail.mail_date <'{end_date}'
                            AND application1_mail.mail_date >'{start_date}')) AS TAB
                            GROUP BY TAB.id,
                                TAB.first_name,
		                        TAB.last_name,
		                        TAB.category,
                                TAB.mail_box
                            HAVING COUNT(*) > 1	
                            ORDER BY occurences DESC
                            LIMIT {lines}
                            """
        cursor=connection.cursor()
        cursor.execute(most_intern_query)
        users=dictfetchall(cursor)

    if req=='prompt response':
        prompt_response_query=f"""SELECT application1_employee.*
                            FROM (SELECT application1_mail_address.*
                                FROM (SELECT DISTINCT application1_mail.sender_mail_id, application1_mail.mail_date-application1_mail.previous_mail_date AS response_time
                                FROM application1_mail
                                WHERE application1_mail.mail_date>application1_mail.previous_mail_date
                                AND application1_mail.mail_date <'{end_date}'
                                AND application1_mail.mail_date >'{start_date}'	  
                                ORDER BY response_time )AS TAB
                                INNER JOIN application1_mail_address
                                ON TAB.sender_mail_id =application1_mail_address.id) AS TAB2
                                INNER JOIN application1_employee
                                ON TAB2.employee_id=application1_employee.id
                                LIMIT {lines}
                            """
        cursor=connection.cursor()
        cursor.execute(prompt_response_query)
        users=dictfetchall(cursor)

    if req=='information distributors':
        information_distributors_query=f"""SELECT application1_employee.*
                                FROM (SELECT application1_mail_address.*
                                FROM (SELECT application1_mail.sender_mail_id,count(application1_mail.sender_mail_id) AS occ
                                FROM application1_mail
                                WHERE  application1_mail.subject NOT LIKE 'Re:%'
                                AND application1_mail.mail_date <'{end_date}'
                                AND application1_mail.mail_date >'{start_date}'	  
                                GROUP BY application1_mail.sender_mail_id
                                ORDER BY occ DESC) AS TAB
                                INNER JOIN application1_mail_address
                                ON TAB.sender_mail_id=application1_mail_address.id) AS TAB2
                                INNER JOIN application1_employee
                                ON TAB2.employee_id=application1_employee.id
                                LIMIT {lines}
                                """
        cursor=connection.cursor()
        cursor.execute(information_distributors_query)
        users=dictfetchall(cursor)


    
    context={
        'users':users,
        'start_date': start_date,
        'end_date'  : end_date,
        'lines' :lines,
        'minimum_threshold':minimum_threshold,
        'maximum_threshold':maximum_threshold        
    }

    return render(request, 'employees.html',context)

def couples(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    lines = request.GET.get('lines')
    minimum_threshold=request.GET.get('minimum_threshold')
    maximum_threshold=request.GET.get('maximum_threshold')
    if not lines:
        lines=10
    if lines:
        pass

    if not start_date:
        start_date= datetime(1999, 1, 1)
    if lines:
        pass


    if not end_date:
        end_date= datetime(2001, 1, 1)
    if lines:
        pass
    #users=Employee.objects.raw('SELECT * FROM application1_employee limit 10')
    couples_query=f"""
                SELECT TAB2.sender_category,TAB2.sender_last_name,TAB2.sender_first_name,application1_employee.category as recipient_category,application1_employee.last_name as recipient_last_name,application1_employee.first_name as recipient_first_name,TAB2.occ
                FROM (SELECT application1_employee.last_name as sender_last_name,application1_employee.first_name as sender_first_name,application1_employee.category as sender_category
                    ,TAB.*
                FROM (SELECT  application1_mail.sender_mail_id, application1_mail.recipient_mail_id, COUNT(*) AS occ 
                FROM application1_mail	
                WHERE application1_mail.mail_date <'{end_date}'
                AND application1_mail.mail_date >'{start_date}'	  
                GROUP BY application1_mail.sender_mail_id, application1_mail.recipient_mail_id
                ORDER BY occ DESC) AS TAB
                INNER JOIN application1_mail_address
                ON TAB.sender_mail_id=application1_mail_address.id
                INNER JOIN application1_employee
                ON application1_employee.id=application1_mail_address.employee_id) AS TAB2
                INNER JOIN application1_mail_address
                ON TAB2.recipient_mail_id=application1_mail_address.id
                INNER JOIN application1_employee
                ON application1_employee.id=application1_mail_address.employee_id
                LIMIT {lines}
                """
    cursor=connection.cursor()
    cursor.execute(couples_query)
    users=dictfetchall(cursor)
    context={
        'users':users,
        'start_date': start_date,
        'end_date'  : end_date,
        'lines' :lines,
        'minimum_threshold':minimum_threshold,
        'maximum_threshold':maximum_threshold        
    }
    return render(request, 'couples.html',context)
    


def days(request):
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    lines = request.GET.get('lines')
    minimum_threshold=request.GET.get('minimum_threshold')
    maximum_threshold=request.GET.get('maximum_threshold')
    if not lines:
        lines=10
    if lines:
        pass

    if not start_date:
        start_date= datetime(1999, 1, 1)
    if lines:
        pass


    if not end_date:
        end_date= datetime(2001, 1, 1)
    if lines:
        pass

    mails_per_day_request=f""" SELECT DATE(application1_mail.mail_date) AS days,COUNT(*) as days_count
        FROM application1_mail
        WHERE mail_date>'{start_date}'
        AND mail_date<'{end_date}'
        GROUP BY days
        ORDER BY days_count desc
        LIMIT {lines}"""
    cursor=connection.cursor()
    cursor.execute(mails_per_day_request)
    days_records=dictfetchall(cursor)    
    
    context={
        'days_records':days_records
    }
    return render(request, 'days.html',context)
"""
def profiles(request):
    #lastname=request.GET.get('nom')
    #firstname=request.GET.get('prénom')

    #if lastname and firstname:
    #    users = Employee.objects.get(first_name=firstname,last_name=lastname)
    
    #else:
    #users=Employee.objects.raw('SELECT * FROM application1_employee limit 10')
    users=Employee.objects.raw('SELECT * FROM application1_employee LIMIT 10')
    context={
        'users':users
    }

    return render(request, 'profiles.html')
"""        
def profiles(request):
    
    
    lastname=request.GET.get('nom')
    firstname=request.GET.get('prénom')

    if lastname and firstname:
        query=f"""SELECT TAB2.first_name,TAB2.last_name,TAB2.category,TAB2.mean_sent_per_day,TAB3.mean_recieved_per_day
FROM(select  TAB.first_name,TAB.last_name,TAB.category,CAST( COUNT(*)AS float)/CAST(365*4 AS FLOAT) as mean_sent_per_day
FROM (SELECT application1_employee.*,application1_mail.* 
FROM application1_mail
INNER JOIN application1_mail_address
ON application1_mail_address.id=application1_mail.sender_mail_id
INNER JOIN application1_employee
ON application1_mail_address.employee_id=application1_employee.id
where application1_employee.first_name='{firstname}' 
AND application1_employee.last_name='{lastname}') AS TAB
GROUP BY TAB.last_name, TAB.first_name,TAB.category) AS TAB2

INNER JOIN (select TAB.last_name,CAST( COUNT(*)AS float)/CAST(365*4 AS FLOAT) as mean_recieved_per_day
FROM (SELECT application1_employee.*,application1_mail.* 
FROM application1_mail
INNER JOIN application1_mail_address
ON application1_mail_address.id=application1_mail.recipient_mail_id
INNER JOIN application1_employee
ON application1_mail_address.employee_id=application1_employee.id
where application1_employee.first_name='{firstname}' 
AND application1_employee.last_name='{lastname}') AS TAB
GROUP BY TAB.last_name, TAB.first_name,TAB.category) AS TAB3
ON TAB2.last_name=TAB3.last_name"""

        cursor=connection.cursor()
        cursor.execute(query)
        users=dictfetchall(cursor)
    
    
    else:
        query=f"""SELECT TAB2.first_name,TAB2.last_name,TAB2.category,TAB2.mean_sent_per_day,TAB3.mean_recieved_per_day
FROM(select  TAB.first_name,TAB.last_name,TAB.category,CAST( COUNT(*)AS float)/CAST(365*4 AS FLOAT) as mean_sent_per_day
FROM (SELECT application1_employee.*,application1_mail.* 
FROM application1_mail
INNER JOIN application1_mail_address
ON application1_mail_address.id=application1_mail.sender_mail_id
INNER JOIN application1_employee
ON application1_mail_address.employee_id=application1_employee.id
where application1_employee.first_name='marie' 
AND application1_employee.last_name='heard') AS TAB
GROUP BY TAB.last_name, TAB.first_name,TAB.category) AS TAB2

INNER JOIN (select TAB.last_name,CAST( COUNT(*)AS float)/CAST(365*4 AS FLOAT) as mean_recieved_per_day
FROM (SELECT application1_employee.*,application1_mail.* 
FROM application1_mail
INNER JOIN application1_mail_address
ON application1_mail_address.id=application1_mail.recipient_mail_id
INNER JOIN application1_employee
ON application1_mail_address.employee_id=application1_employee.id
where application1_employee.first_name='marie' 
AND application1_employee.last_name='heard') AS TAB
GROUP BY TAB.last_name, TAB.first_name,TAB.category) AS TAB3
ON TAB2.last_name=TAB3.last_name"""
        cursor=connection.cursor()
        cursor.execute(query)
        users=dictfetchall(cursor)
    context={
        'users':users
    }
    return render(request, 'profiles.html',context)    
    
    
   