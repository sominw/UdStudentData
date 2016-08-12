# -*- coding: utf-8 -*-
"""
Basic Data Analysis
@author: sominwadhwa

Note: Originally created in Anaconda/spyder (Python 2.7). Do the required modifications
if running on a different enviroment.
"""
import unicodecsv
from datetime import datetime as dt
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def file_info(filename):
    with open(filename,'rb') as f:
        reader = unicodecsv.DictReader(f)
        file_list = list(reader)
        return file_list
    
enrollments = file_info('/Users/sominwadhwa/Work/Python Files/UdStudentData/enrollments.csv')
daily_engagement = file_info('/Users/sominwadhwa/Work/Python Files/UdStudentData/daily_engagement.csv')
project_submissions = file_info('/Users/sominwadhwa/Work/Python Files/UdStudentData/project_submissions.csv')

#Takes a string, returns python datetime project. Returns none is empty string is passed.
def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

#Takes a string that represents an integer & returns the same integer
def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)

for engagements in daily_engagement:
    engagements['account_key'] = engagements['acct']
    del engagements['acct']

#Cleaning data in enrollments
for enrollment in enrollments: 
    enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
    enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
    enrollment['join_date'] = parse_date(enrollment['join_date'])
    
#Cleaning data for daily_engagements
for engagement_record in daily_engagement:
    engagement_record['lessons_completed'] = int(float(engagement_record['lessons_completed']))
    engagement_record['num_courses_visited'] = int(float(engagement_record['num_courses_visited']))
    engagement_record['projects_completed'] = int(float(engagement_record['projects_completed']))
    engagement_record['total_minutes_visited'] = float(engagement_record['total_minutes_visited'])
    engagement_record['utc_date'] = parse_date(engagement_record['utc_date'])

#Cleaning data for project_submissions    
for submission in project_submissions:
    submission['completion_date'] = parse_date(submission['completion_date'])
    submission['creation_date'] = parse_date(submission['creation_date'])

print (enrollments[0]);
print (daily_engagement[0]);
print (project_submissions[0]);

def unique_students(data):
    unique_student = set()
    for enrolled in data:
        unique_student.add(enrolled['account_key'])
    return unique_student

print "\n\nTotal Enrollments : ",len(enrollments)
unique_enrolled_students = unique_students(enrollments)
print "Unique Enrollments : ",len(unique_enrolled_students)

print "Daily Engagements: ",len(daily_engagement)
unique_engagement_students = unique_students(daily_engagement)
print "Unique Daily Engagemets: ",len(unique_engagement_students)

print "Project Submissions: ",len(project_submissions)
unique_project_submitters = unique_students(project_submissions)
print "Unique Project Submissions: ",len(unique_project_submitters)

#Printing enrollment not in unique daily engagement i.e : Unusual records
for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_engagement_students:
        print enrollment
        break

#Checking for more problematic records
num_problem_students = 0
for enrollment in enrollments:
    student = enrollment['account_key']
    if (student not in unique_engagement_students and 
            enrollment['join_date'] != enrollment['cancel_date']):
        print enrollment
        num_problem_students += 1

print "\n\n\nUnusal Records", num_problem_students

#Noticed that all the unusual records were udacity test accounts
udacity_test_accounts = set()
for enrollment in enrollments:
    if (enrollment['is_udacity']):
        udacity_test_accounts.add(enrollment['account_key'])
    
print "Udacity Test Accounts (bots): ", len(udacity_test_accounts), "\n\n"

#Identifying actual user records (removing udacity bots)
def remove_udacity_accounts(data):
    non_udacity_data = []
    for data_point in data:
        if(data_point['account_key'] not in udacity_test_accounts):
            non_udacity_data.append(data_point)
        
    return non_udacity_data

non_udacity_enrollments = remove_udacity_accounts(enrollments)
non_udacity_engagements = remove_udacity_accounts(daily_engagement)
non_udacity_submissions = remove_udacity_accounts(project_submissions)

print "Data set without udacity bots is: \n"
print "Enrollments: ", len(non_udacity_enrollments)
print "Daily Engagements: ", len(non_udacity_engagements)
print "Project Submissions: ", len(non_udacity_submissions)

#How daily engagements differ from first project completion
paid_students = {}
for enrollment in non_udacity_enrollments:
    if (not enrollment['is_udacity'] or enrollment['days_to_cancel'] > 7):
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
    if (account_key not in paid_students or enrollment_date > paid_students[account_key]):
        paid_students[account_key] = enrollment_date

print "\n\nTotal number of paid students: ",len(paid_students)

#Getting data from the first week (Time)
def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0

def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_engagement = remove_free_trial_cancels(non_udacity_engagements)
paid_submissions = remove_free_trial_cancels(non_udacity_submissions)

print "\n\nPaid Enrollments: ",len(paid_enrollments)
print "Paid Engagements: ",len(paid_engagement)
print "Paid Submissions: " ,len(paid_submissions)

for engagement_record in paid_engagement:
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0

paid_engagement_in_first_week = []
for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_record_date):
        paid_engagement_in_first_week.append(engagement_record)

print "\n\nPaid engagements in first week: ",len(paid_engagement_in_first_week)

#Evaluating student engagement: Avg minutes spent in the classroom 
def group_data(data,key_name):
    grouped_data = defaultdict(list) #Returns empty list when no values are present
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data
engagement_by_account = group_data(paid_engagement_in_first_week,'account_key')

#Calculation of minutes using NUMPY 
def summed_grouped_data_items(grouped_data,field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

total_minutes_by_account = summed_grouped_data_items(engagement_by_account, 'total_minutes_visited')

def describe_data(data):
    print "Average: ",np.mean(data)
    print "Standard Deviation: ", np.std(data)
    print "Maximum: ",np.max(data)
    print "Minimum: ",np.min(data)
    plt.hist(data)
    plt.show()

print "\nTime analysis for the first week for paid enrollments: "
describe_data(total_minutes_by_account.values())

#Debugging maximum no. of minutes
#Problem was traced back to within_one_week fn, and corrected by adding
#time_delta.days >= 0 to the return statement

#Analysing lessons completed in one week
lessons_completed_by_account = summed_grouped_data_items(engagement_by_account, 'lessons_completed')

print "\nLesson completion analysis for the first week for paid enrollments: "
describe_data(lessons_completed_by_account.values())

#Analysing num_courses_visted/days
days_visted_by_account = summed_grouped_data_items(engagement_by_account,'has_visited')
print "\nAnalysing days visted: "
describe_data(days_visted_by_account.values())

#Splitting students based on their passing of projects (1)
subway_project_lesson_keys = ['746169184','3176718735']
pass_subway_project = set()
for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating'] 
    if ((project in subway_project_lesson_keys) and (rating == 'PASSED' or rating == 'DISTINCTION')):
        pass_subway_project.add(submission['account_key'])
print "\nTotal number of students who passed the subway project: ",len(pass_subway_project)
passing_engagement = []
non_passing_engagement = []
for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)
print "Passing engagement: ",len(passing_engagement)
print "Non passing engagement: ",len(non_passing_engagement)

#Comparing groups of students who pass with the ones who dont't
print"\nComparing groups of students: " 
passing_engagement_by_account = group_data(passing_engagement,'account_key')
non_passing_engagement_by_account = group_data(non_passing_engagement,'account_key')
print "\nFor non-passing student: \n"
print "Minutes Visted: "
non_passing_minutes = summed_grouped_data_items(
    non_passing_engagement_by_account,
    'total_minutes_visited'
)
describe_data(non_passing_minutes.values())
print "Lessons Completed: "
non_passing_lessons = summed_grouped_data_items(
    non_passing_engagement_by_account,
    'lessons_completed'
)
describe_data(non_passing_lessons.values())
print 'Number of visits: '
non_passing_visits = summed_grouped_data_items(
    non_passing_engagement_by_account, 
    'has_visited'
)
describe_data(non_passing_visits.values())
print ("\nFor Passing students: \n")
print "Minutes Visited: "
passing_minutes = summed_grouped_data_items(
    passing_engagement_by_account,
    'total_minutes_visited'
)
describe_data(passing_minutes.values())
print "Lessons Completed: "
passing_lessons = summed_grouped_data_items(
    passing_engagement_by_account,
    'lessons_completed'
)
describe_data(passing_lessons.values())
print "Number of visits: "
passing_visits = summed_grouped_data_items(
    passing_engagement_by_account,
    'has_visited'
)
describe_data(passing_visits.values())

