from bs4 import BeautifulSoup
import boto3
import requests
import json
from urllib import parse
from dotenv import load_dotenv
import os

# load .env
load_dotenv()


class WishketbotV2:
    def __init__(self):
        # S3
        self.bucket_name = os.environ.get("MY_BUCKET_NAME")
        self.bucket_key = os.environ.get("MY_BUCKET_KEY")
        self.s3 = boto3.resource("s3")
        self.s3_object = self.s3.Object(self.bucket_name, self.bucket_key)
        # telegram
        self.base_telegram_url = os.environ.get("TELEGRAM_URL")
        # bs4
        self.json_array = []
        self.base_url = "https://www.wishket.com"
        self.choice_dev_project_url = "/project/?d=M4JwLgvAdgpg7kA%3D"
        self.base_project_info_div = "div > section.project-organic-info"
        self.selector_links = self.base_project_info_div + " > a"
        self.selector_titles = self.base_project_info_div + " > a > p"
        self.selector_budgets = (
            self.base_project_info_div
            + " > div.project-core-info.mb10 > p.budget.body-1.text700 > span"
        )
        self.selector_terms = (
            self.base_project_info_div
            + " > div.project-core-info.mb10 > p.term.body-1.text700 > span"
        )
        self.selector_pj_type = (
            self.base_project_info_div
            + " > div.project-minor-info > div.project-status-label.recruiting-status > div"
        )
        self.selector_skills = (
            self.base_project_info_div
            + " > div.project-minor-info > div.project-skills-info > span"
        )
        self.selector_locations = (
            self.base_project_info_div
            + " > div.project-minor-info > p.body-3.text500.location-data"
        )

    def start(self):
        html = requests.get(self.base_url + self.choice_dev_project_url).text
        soup = BeautifulSoup(html, "lxml")
        old_data = self.get_old_data()
        project_info_boxes = soup.select("#projectListView>div>div")
        for project_info_box in project_info_boxes:
            link = project_info_box.select_one(self.selector_links)["href"]
            link = self.base_url + link
            print(old_data[0]["link"])
            print(link)

            # 이전 데이터와 비교
            # 가장 마지막에 긁어온 프로젝트의 링크와 지금 긁어오는 데이터와 같으면 그 이후 데이터 무시
            if old_data[0]["link"] == link:
                break

            title = project_info_box.select_one(self.selector_titles).text
            print(title)
            budget = project_info_box.select_one(self.selector_budgets).text
            term = project_info_box.select_one(self.selector_terms).text
            pj_type = project_info_box.select_one(self.selector_pj_type).text
            skills = [
                skill.text for skill in project_info_box.select(self.selector_skills)
            ]
            location = (
                project_info_box.select_one(self.selector_locations).text
                if project_info_box.select_one(self.selector_locations) is not None
                else ""
            )

            pj_obj = {
                "title": title,
                "budget": budget,
                "term": term,
                "pjType": pj_type,
                "skills": " ".join(skills),
                "location": location,
                "link": link,
            }
            print(pj_obj)
            self.json_array.append(pj_obj)

        print(self.json_array)

        # S3에 업로드
        self.save_new_projects(self.json_array)
        # 텔레그램으로 보내기
        self.sendTelegram(self.json_array)

    def sendTelegram(self, projects):
        # newest is latest
        if len(projects) == 0:
            return
        for pj in list(reversed(projects)):
            pj = list(pj.values())
            pj = f"{pj[0]}\n{pj[1]}\n{pj[2]}\n{pj[3]} / {pj[4]}\n{pj[5]}\n{pj[6]}"
            requests.post(self.base_telegram_url + parse.quote(pj))

    def get_old_data(self):
        old_data = self.s3_object.get()["Body"].read().decode("utf-8")
        old_projects = json.loads(old_data)
        return old_projects

    def save_new_projects(self, data):
        if len(data) == 0:
            return
        json_data = json.dumps(data, indent=4)
        self.s3_object.put(Body=json_data)


def lambda_handler(event, context):
    print("start crawler.")
    print("start crawler..")
    print("start crawler...")

    crawler = WishketbotV2()
    crawler.start()


crawler = WishketbotV2()
crawler.start()
