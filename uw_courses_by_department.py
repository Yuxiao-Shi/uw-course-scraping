import requests
import re
import os
from bs4 import BeautifulSoup
from csv import writer

quarter = 'WIN2021'
root_url = 'https://www.washington.edu/students'
time_sched_home = root_url + '/timeschd/' + quarter + '/'
response = requests.get(time_sched_home)
soup = BeautifulSoup(response.text, 'html.parser')


def department_match(tag):
    '''
    Filters out the department course home pages.

    Param: the HTML object tag.
    Returns: True if tag has attribute 'href' and its text content ends with
    departement abbreviations enclosed in parenthesis.
    Example matched text content: Afro-American Studies (AFRAM)
    '''
    return tag.has_attr('href') and re.search(".*\((.*)\)", tag.get_text())


departements = soup.find_all(department_match)
departements = set(departements)
for d in departements:
    department_name = d.get_text().replace(u'\xa0', ' ')
    department_abbr = re.search(".*\((.*)\)", department_name).group(1)
    department_abbr = department_abbr.replace(u'\xa0', ' ')
    d_url_short = d['href']
    department_url = time_sched_home + d['href']

    '''
    Create a department csv
    '''
    dir_name = 'courses_by_department_' + quarter.lower()
    csv_file_name = department_abbr + '_courses_' + quarter.lower() + '_UW.csv'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("Directory ", dir_name, " Created ")
    with open(dir_name + '/' + csv_file_name, 'w', newline='') as csv_file:
        csv_writer = writer(csv_file)
        headers = [
            'department_name',
            'department_abbr',
            'department_url',
            'course_num',
            'course_name',
            'course_credit_type',
            'course_myplan_url']
        csv_writer.writerow(headers)

        '''
        Courses
        '''
        def course_match(tag):
            course_url_pattern = r'^/students/crscat/'
            # re.search("^[A-Z]{2,}", tag.get_text())
            return tag.has_attr('href') and re.search(course_url_pattern, tag['href'])
        department_response = requests.get(department_url)
        d_soup = BeautifulSoup(department_response.text, 'html.parser')

        courses = d_soup.find_all(course_match)
        for course in courses:
            course_name = course.get_text().replace(u'\xa0', ' ')  # e.g. COMPUTER PRGRMNG I
            course_num = re.sub(r'\s+', '', course.find_previous_sibling().get_text())
            course_num = course_num.replace(u'\xa0', ' ')  # e.g. CSE142
            course_myplan_url = 'https://myplan.uw.edu/course/#/courses/' + course_num

            '''
            Dynamic url update & course description # TODO
                d_url_short = 'cse.html'  # TODO
                # e.g. https://www.washington.edu/students/crscat/cse.html#cse142
                course_url = root_url + '/crscat/' + d_url_short + '#' + course_num.lower()
                cd_response = requests.get(course_url)
                cd_soup = BeautifulSoup(cd_response.text, 'html.parser')

                def cd_match(name):
                    return name and name == course_num.lower()

                cd_a = cd_soup.find(name=cd_match)
                course_description = cd_a.find('br').get_text()

                # e.g. https://myplan.uw.edu/course/#/courses/CSE142
                course_myplan_url = cd_a.find_next_sibling()['href']
                print(course_myplan_url)
                # course_num = table.find_all('a')[0].get_text()
                # print(course_num)
            '''
            course_credit_type = course.find_parent('td').find_next_sibling().find('b').get_text()
            course_credit_type = course_credit_type.replace(u'\xa0', ' ')
            if (re.search("\((.*)\)", course_credit_type) is not None):
                # get rid of the parenthesis
                course_credit_type = re.search("\((.*)\)", course_credit_type).group(1)

            row = [
                department_name,
                department_abbr,
                department_url,
                course_num,
                course_name,
                course_credit_type,
                course_myplan_url]
            for str in row:
                str = str.replace(u'\xa0', ' ')

            csv_writer.writerow(row)
        print(department_name)

# def write_courses_to_csv(csv_writer, department_url):
