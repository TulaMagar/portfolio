"""
Module for serving views to user
"""

import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

import psycopg2
from faker import Faker
from openpyxl import load_workbook
from .decorators import unauthenticated_user, allowed_users


@login_required(login_url='/registration/login/')
def home(request):
    """
    Serves homepage to user based on request
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    if request.method == 'POST':
        if request.POST.get('RowData'):
            boxes = (
                'Last Name', 'First Name',
                'Student ID', 'UNH ID',
                'Major Name', 'Degree Name',
                'School Email', 'LinkedIn URL',
                'Course ID', 'Credits',
                'Semester', 'Year',
                'Instructor', 'Internship ID',
                'Internship Position', 'Pay',
                'Start Date', 'End Date',
                'Organization', 'Organization URL',
                'Organization Address', 'Supervisor Name',
                'Supervisor Position', 'Supervisor Email',
                'Supervisor Phone'
            )
            fields_dict = {
                'TableRow_fields': boxes
            }
            return render(request, 'add_entry.html', fields_dict)
        if request.POST.get('add'):
            student_sql = '''
                          INSERT INTO student (
                              student_id, unh_id, last_name, first_name,
                              school_email, major, degree, linkedin_url
                          )
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                          '''
            student = (request.POST.get('3'), request.POST.get('4'),
                       request.POST.get('1'), request.POST.get('2'),
                       request.POST.get('7'), request.POST.get('5'),
                       request.POST.get('6'), request.POST.get('8'))
            cursor.execute(student_sql, student)
            connection.commit()
            internship_sql = '''
                             INSERT INTO internship (
                                 internship_id, position,
                                 pay, organization_name,
                                 organization_url, organization_address,
                                 supervisor_name, supervisor_position,
                                 supervisor_email, supervisor_phone
                             )
                             VALUES(%s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s)
                             '''
            internship = (request.POST.get('14'), request.POST.get('15'),
                          request.POST.get('16'), request.POST.get('19'),
                          request.POST.get('20'), request.POST.get('21'),
                          request.POST.get('22'), request.POST.get('23'),
                          request.POST.get('24'), request.POST.get('25'))
            cursor.execute(internship_sql, internship)
            connection.commit()
            internship_assignment_sql = '''
                                        INSERT INTO internship_assignment (
                                            student_id, internship_id,
                                            course_id, credits,
                                            semester, year,
                                            instructor, start_date,
                                            end_date
                                        )
                                        VALUES (%s, %s, %s, %s, %s,
                                                %s, %s, %s, %s)
                                        '''
            internship_assign = (request.POST.get('3'), request.POST.get('14'),
                                 request.POST.get('9'), request.POST.get('10'),
                                 request.POST.get('11'), request.POST.get('12'),
                                 request.POST.get('13'), request.POST.get('17'),
                                 request.POST.get('18'))
            cursor.execute(internship_assignment_sql, internship_assign)
            connection.commit()
    return render(request, 'index.html')

@unauthenticated_user
def login(request):
    """
    Creates login view
    Returns: rendered login page
    """
    return render(request, 'registration/login.html')

def register(response):
    """
    Creates new user from registration page
    Returns: rendered register page
    """
    if response.method == "POST":
        form = UserCreationForm(response.POST)
        if form.is_valid():
            user = form.save()
            if response.POST.get('group') == 'current':
                group = Group.objects.get(name='Current Student')
            if response.POST.get('group') == 'future':
                group = Group.objects.get(name='Future Student')
            user.groups.add(group)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(response, 'registration/register.html', {"form":form})

@allowed_users(allowed_roles=['Internship Coordinator'])
def upload_spreadsheet(request):
    """
    Creates database tables from uploaded file spreadsheet and populates
    missing data using Faker data
    Returns: rendered upload view
    """
    if request.method == 'POST':
        if request.FILES.get('document'):
            file = request.FILES['document']
            workbook = load_workbook(filename=file, data_only=True)
            xls = workbook[workbook.sheetnames[0]]
            connection = connect_to_db()
            sql_create_student_table = """ CREATE TABLE IF NOT EXISTS student (
                                               student_id text PRIMARY KEY,
                                               unh_id text,
                                               last_name text,
                                               first_name text,
                                               school_email text,
                                               major text,
                                               degree text,
                                               linkedin_url text,
                                               update text,
                                               delete text
                                               ); """
            sql_create_int_assign_table = """ CREATE TABLE IF NOT EXISTS
                                                       internship_assignment (
                                                       student_id text,
                                                       internship_id text,
                                                       course_id text,
                                                       credits text,
                                                       semester text,
                                                       year text,
                                                       instructor text,
                                                       start_date text,
                                                       end_date text,
                                                       update text,
                                                       delete text,
                                                       PRIMARY KEY
                                                       (student_id,
                                                        internship_id)
                                                       ); """
            sql_create_internship_table = """ CREATE TABLE IF NOT EXISTS
                                               internship (
                                               internship_id text PRIMARY KEY,
                                               position text,
                                               pay text,
                                               organization_name text,
                                               organization_url text,
                                               organization_address text,
                                               supervisor_name text,
                                               supervisor_position text,
                                               supervisor_email text,
                                               supervisor_phone text,
                                               update text,
                                               delete text
                                               ); """
            fake = Faker()
            if connection is not None:
                create_table(connection, sql_create_student_table)
                create_table(connection, sql_create_int_assign_table)
                create_table(connection, sql_create_internship_table)

                num_rows = xls.max_row
                while True:
                    if xls.cell(num_rows, 3).value is not None:
                        break
                    else:
                        num_rows -= 1
                for i in range(2, num_rows+1):
                    student = (fake.ean(length=8), fake.ean(length=8),
                               fake.last_name(), fake.first_name(),
                               fake.free_email(), xls['D'+str(i)].value,
                               xls['E'+str(i)].value, fake.url(['https']),
                               '', '')
                    create_student(connection, student)
                    internship_assignment = (fake.ean(length=8),
                                             fake.ean(length=8),
                                             xls['I'+str(i)].value,
                                             xls['J'+str(i)].value,
                                             xls['K'+str(i)].value,
                                             xls['L'+str(i)].value,
                                             xls['M'+str(i)].value,
                                             xls['P'+str(i)].value,
                                             xls['Q'+str(i)].value,
                                             '',
                                             '')
                    create_internship_assignment(connection,
                                                 internship_assignment)
                    internship = (fake.ean(length=8), xls['N'+str(i)].value,
                                  xls['O'+str(i)].value, xls['R'+str(i)].value,
                                  fake.url(['https']), xls['T'+str(i)].value,
                                  xls['X'+str(i)].value, xls['Y'+str(i)].value,
                                  xls['Z'+str(i)].value, xls['AA'+str(i)].value,
                                  '', '')
                    create_internship(connection, internship)

            else:
                print("Error - cannot create the database tables.")
    return render(request, 'upload.html')

def create_table(conn, create_table_sql):
    """
    Creates a database table
    Inputs: database connection, SQL for table creation
    """
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
    except psycopg2.OperationalError as error:
        print(error)

def create_student(conn, student):
    """
    Inserts into student table using SQL
    Inputs: database connection and student tuple
    Returns: auto increment value property of row
    """
    sql = ''' INSERT INTO student(student_id, unh_id, last_name, first_name,
                                  school_email, major, degree, linkedin_url,
                                  update, delete)
              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur = conn.cursor()
    cur.execute(sql, student)
    conn.commit()
    return cur.lastrowid

def create_internship_assignment(conn, internship_assignment):
    """
    Inserts into internship assignment table using SQL
    Inputs: database connection and internship assignment tuple
    Returns: auto increment value property of row
    """
    sql = '''INSERT INTO internship_assignment(student_id, internship_id,
                                               course_id, credits,
                                               semester, year,
                                               instructor, start_date,
                                               end_date, update,
                                               delete)
              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur = conn.cursor()
    cur.execute(sql, internship_assignment)
    conn.commit()
    return cur.lastrowid

def create_internship(conn, internship):
    """
    Inserts into internship table using SQL
    Inputs: database connection and internship tuple
    Returns: auto increment value property of row
    """
    sql = ''' INSERT INTO internship(internship_id, position,
                                  pay, organization_name,
                                  organization_url, organization_address,
                                  supervisor_name, supervisor_position,
                                  supervisor_email, supervisor_phone,
                                  update, delete)
              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur = conn.cursor()
    cur.execute(sql, internship)
    conn.commit()
    return cur.lastrowid

def connect_to_db():
    """
    Creates a connection to the database
    Returns database connection
    """
    if 'ON_HEROKU' in os.environ:
        connection = psycopg2.connect(os.environ['DATABASE_URL'],
                                      sslmode='require')
    else:
        connection = psycopg2.connect(dbname="internship",
                                      user="postgres",
                                      password="Computer",
                                      host="127.0.0.1",
                                      port="5432")
    return connection

@allowed_users(allowed_roles=['Internship Coordinator'])
def display_students(request):
    """
    Displays the students table, add, update, or delete function based on
    user request
    Returns the appropriate HTML page
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    if request.method == 'POST':
        student_id = request.POST.get('id')
        if request.POST.get('update'):
            results = (request.POST.get('student_id'),
                       request.POST.get('unh_id'),
                       request.POST.get('last_name'),
                       request.POST.get('first_name'),
                       request.POST.get('school_email'),
                       request.POST.get('major'),
                       request.POST.get('degree'),
                       request.POST.get('linkedin_url'))
            results_dict = {
                'students': results
            }
            return render(request, 'update_student.html', results_dict)
        if request.POST.get('student'):
            boxes = ('Student ID', 'UNH ID', 'Last Name', 'First Name',
                     'School Email', 'Major', 'Degree', 'LinkedIn URL')
            fields_dict = {
                'student_fields': boxes
            }
            return render(request, 'add_entry.html', fields_dict)
        if request.POST.get('add'):
            sql = '''INSERT INTO student(student_id, unh_id,
                                         last_name, first_name,
                                         school_email, major,
                                         degree, linkedin_url)
                      VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'''
            student = (request.POST.get('1'), request.POST.get('2'),
                       request.POST.get('3'), request.POST.get('4'),
                       request.POST.get('5'), request.POST.get('6'),
                       request.POST.get('7'), request.POST.get('8'),)
            cursor.execute(sql, student)
            connection.commit()
        if request.POST.get('finalize'):
            sql = f'''UPDATE student
                      SET unh_id = \'{request.POST.get('unh_id')}\',
                          last_name = \'{request.POST.get('last_name')}\',
                          first_name = \'{request.POST.get('first_name')}\',
                          school_email = \'{request.POST.get('school_email')}\',
                          major = \'{request.POST.get('major')}\',
                          degree = \'{request.POST.get('degree')}\',
                          linkedin_url = \'{request.POST.get('linkedin_url')}\'
                      WHERE student_id = \'{request.POST.get('student_id')}\';
                   '''
            cursor.execute(sql)
            connection.commit()
        if request.POST.get('delete'):
            sql = f'DELETE FROM student WHERE student_id = \'{student_id}\';'
            cursor.execute(sql)
            connection.commit()
    sql = 'SELECT * FROM student;'
    cursor.execute(sql)
    results = cursor.fetchall()
    results_dict = {
        'students': results
    }
    cursor.close()
    connection.close()
    return render(request, 'display_student.html', results_dict)

@allowed_users(allowed_roles=['Internship Coordinator',
                              'Current Student',
                              'Future Student'])
def display_internships(request):
    """
    Displays the internships table, update, delete, or add page based on
    user request
    Returns the appropriate HTML page
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    if request.method == 'POST':
        internship_id = request.POST.get('id')
        if request.POST.get('update'):
            results = (request.POST.get('internship_id'),
                       request.POST.get('position'),
                       request.POST.get('pay'),
                       request.POST.get('organization_name'),
                       request.POST.get('organization_url'),
                       request.POST.get('organization_address'),
                       request.POST.get('supervisor_name'),
                       request.POST.get('supervisor_position'),
                       request.POST.get('supervisor_email'),
                       request.POST.get('supervisor_phone'))
            results_dict = {
                'internships': results
            }
            return render(request, 'update_internship.html', results_dict)
        if request.POST.get('internship'):
            boxes = ('Internship ID', 'Position',
                     'Pay', 'Organization Name',
                     'Organization URL', 'Organization Address',
                     'Supervisor Name', 'Supervisor Position',
                     'Supervisor Email', 'Supervisor Phone')
            fields_dict = {
                'internship_fields': boxes
            }
            return render(request, 'add_entry.html', fields_dict)
        if request.POST.get('add'):
            sql = '''
                  INSERT INTO internship(internship_id, position,
                                         pay, organization_name,
                                         organization_url, organization_address,
                                         supervisor_name, supervisor_position,
                                         supervisor_email, supervisor_phone)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  '''
            student = (request.POST.get('1'), request.POST.get('2'),
                       request.POST.get('3'), request.POST.get('4'),
                       request.POST.get('5'), request.POST.get('6'),
                       request.POST.get('7'), request.POST.get('8'),
                       request.POST.get('9'), request.POST.get('10'))
            cursor.execute(sql, student)
            connection.commit()
        if request.POST.get('finalize'):
            sql = f'''UPDATE internship
                      SET position = \'{request.POST.get('position')}\',
                          pay = \'{request.POST.get('pay')}\',
                          organization_name = \'{request.POST.get('organization_name')}\',
                          organization_url = \'{request.POST.get('organization_url')}\',
                          organization_address = \'{request.POST.get('organization_address')}\',
                          supervisor_name = \'{request.POST.get('supervisor_name')}\',
                          supervisor_position = \'{request.POST.get('supervisor_position')}\',
                          supervisor_email = \'{request.POST.get('supervisor_email')}\',
                          supervisor_phone = \'{request.POST.get('supervisor_phone')}\'
                      WHERE internship_id = \'{request.POST.get('internship_id')}\';
                   '''
            cursor.execute(sql)
            connection.commit()
        if (request.POST.get('delete') and
                request.user.groups.get().name == 'Internship Coordinator'):
            sql = f'''DELETE FROM internship
                      WHERE internship_id = \'{internship_id}\';'''
            cursor.execute(sql)
            connection.commit()
        elif (request.POST.get('delete') and
              request.user.groups.get().name != 'Internship Coordinator'):
            return render(request, 'bad_role.html')
        else:
            pass
    sql = 'SELECT * FROM internship;'
    cursor.execute(sql)
    results = cursor.fetchall()
    results_dict = {
        'internships': results
    }
    cursor.close()
    connection.close()
    return render(request, 'display_internship.html', results_dict)

@allowed_users(allowed_roles=['Internship Coordinator'])
def display_internship_assignments(request):
    """
    Displays the internship assignments table, delete, add, or update
    button based on user request
    Returns the appropriate HTML page
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    if request.method == 'POST':
        student_id = request.POST.get('id')
        if request.POST.get('update'):
            results = (request.POST.get('student_id'),
                       request.POST.get('internship_id'),
                       request.POST.get('course_id'),
                       request.POST.get('credits'),
                       request.POST.get('semester'),
                       request.POST.get('year'),
                       request.POST.get('instructor'),
                       request.POST.get('start_date'),
                       request.POST.get('end_date'))
            results_dict = {
                'internship_assignments': results
            }
            return render(request, 'update_internship_assignment.html',
                          results_dict)
        if request.POST.get('internship_assignment'):
            boxes = ('Student ID', 'Internship ID',
                     'Course ID', 'Credits',
                     'Semester', 'Year',
                     'Instructor', 'Start Date',
                     'End Date')
            fields_dict = {
                'internship_assignment_fields': boxes
            }
            return render(request, 'add_entry.html', fields_dict)
        if request.POST.get('add'):
            sql = '''
                  INSERT INTO internship_assignment(student_id, internship_id,
                                                    course_id, credits,
                                                    semester, year,
                                                    instructor, start_date,
                                                    end_date)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                  '''
            student = (request.POST.get('1'), request.POST.get('2'),
                       request.POST.get('3'), request.POST.get('4'),
                       request.POST.get('5'), request.POST.get('6'),
                       request.POST.get('7'), request.POST.get('8'),
                       request.POST.get('9'))
            cursor.execute(sql, student)
            connection.commit()
        if request.POST.get('finalize'):
            sql = f'''UPDATE internship_assignment
                      SET course_id = \'{request.POST.get('course_id')}\',
                          credits = \'{request.POST.get('credits')}\',
                          semester = \'{request.POST.get('semester')}\',
                          year = \'{request.POST.get('year')}\',
                          instructor = \'{request.POST.get('instructor')}\',
                          start_date = \'{request.POST.get('start_date')}\',
                          end_date = \'{request.POST.get('end_date')}\'
                      WHERE student_id = \'{request.POST.get('student_id')}\';
                   '''
            cursor.execute(sql)
            connection.commit()
        if request.POST.get('delete'):
            sql = f'''DELETE FROM internship_assignment
                     WHERE student_id = \'{student_id}\';'''
            cursor.execute(sql)
            connection.commit()
    sql = 'SELECT * FROM internship_assignment;'
    cursor.execute(sql)
    results = cursor.fetchall()
    results_dict = {
        'internship_assignments': results
    }
    cursor.close()
    connection.close()
    return render(request, 'display_internship_assignment.html', results_dict)
