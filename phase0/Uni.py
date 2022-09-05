from BaseCrawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('__main__')


class GLA(BaseCrawler):
    Course_Page_Url = "https://www.gla.ac.uk/coursecatalogue/browsebysubjectarea/"
    University = "University of Glasglow"
    Abbreviation = "GLA"
    University_Homepage = "https://www.gla.ac.uk"

    # Below fields didn't find in the website
    Prerequisite = None
    References = None
    Scores = None
    Projects = None
    Professor_Homepage = None

    def get_courses_of_department(self, subject):
        subject_Name = subject.find('a').get('title')
        subject_Homepage = "https://www.gla.ac.uk" + subject.find('a').get('href')
        subject_html_content = requests.get(subject_Homepage).text
        subject_soup = BeautifulSoup(subject_html_content, 'html.parser')

        courses_html_content = subject_soup.find(id='main-content-wrapper')

        courses = []
        # subject_Name = courses_html_content.find('h1').text.strip()


        courses_by_levels = courses_html_content.find('form', id='printForm').find_all('ul')
        for courses_by_level in courses_by_levels:
            courses.extend(courses_by_level.find_all('li'))
        return courses, subject_Name

    def get_course_data(self,course):
        # course_name = course.find('a').text
        course_homepage = "https://www.gla.ac.uk" + course.find('a').get('href')
        course_html_content = requests.get(course_homepage).text
        course_soup = BeautifulSoup(course_html_content, 'html.parser')
        course = course_soup.find(id='main-content-wrapper')

        course_Title = course.find('h2').text


        course_info = course.find('ul').find_all('li')

        for info in course_info:
            parts = info.text.split(':')
            if parts[0] == "Academic Session":
                course_year = parts[1]
            elif parts[0] == "School":
                course_school = parts[1]


        course_details = course.find('div').find_all('div')[1:]

        course_headers = course.find_all('h3')
        course_headers_count = 0
        course_Description = None
        Required_Skills = None
        Objective = None
        Outcome = None

        for course_header in course_headers:
            if course_header.text.strip().lower() == 'short description':
                course_Description = course_details[course_headers_count].text.strip()
            elif course_header.text.strip().lower() == 'requirements of entry':
                Required_Skills = course_details[course_headers_count].text.strip()
            elif course_header.text.strip().lower() == 'course aims':
                Objective = course_details[course_headers_count].text.strip()
            elif course_header.text.strip().lower() == 'intended learning outcomes of course':
                Outcome = course_details[course_headers_count].text.strip()

            course_headers_count = course_headers_count + 1


        # course_Description = course_details[2].text.strip()
        # course_time = course_details[3].find('p').text.strip()
        # Required_Skills = course_details[4].text.strip()
        # Objective = course_details[7].text.strip()
        # Outcome = course_details[8].text.strip()

        Unit_Count = None
        Professor = None


        return course_homepage, course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, course_Description

    def handler(self):
        html_content = requests.get(self.Course_Page_Url).text
        soup = BeautifulSoup(html_content, 'html.parser')

        subjects = soup.find(id='main-content-wrapper').find_all('li')


        course_count = 0
        subject_count = 0
        print("subjects count: " + str(len(subjects)))
        for subject in subjects:
            subject_count = subject_count + 1
            courses, Department_Name = self.get_courses_of_department(subject)
            for course in courses:
                course_count = course_count + 1
                Course_Homepage, Course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, Description = self.get_course_data(course)

                self.save_course_data(
                    self.University, self.Abbreviation, Department_Name, Course_Title, Unit_Count,
                    Professor, Objective, self.Prerequisite, Required_Skills, Outcome, self.References, self.Scores,
                    Description, self.Projects, self.University_Homepage, Course_Homepage, self.Professor_Homepage
                )
                print("course " + str(course_count) + " added")
            print("subject " + str(subject_count) + " added")
            logger.info(f"{self.Abbreviation}: {Department_Name} department's data was crawled successfully.")

        logger.info(f"{self.Abbreviation}: Total {self.course_count} courses were crawled successfully.")