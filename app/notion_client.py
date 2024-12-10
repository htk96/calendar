import requests
from .config import Config
from flask import current_app

class NotionClient:
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {Config.NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.database_id = Config.NOTION_DATABASE_ID

    def _handle_response(self, response):
        """Handle API response and raise exceptions for errors"""
        if not response.ok:
            error = response.json()
            raise Exception(f"Notion API error: {error.get('message', 'Unknown error')}")
        return response.json()

    def get_projects(self):
        url = f"{self.base_url}/databases/{self.database_id}/query"
        response = requests.post(url, headers=self.headers)
        return self._handle_response(response)

    def create_project(self, title, start_date, end_date, status="진행중"):
        url = f"{self.base_url}/pages"
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "이름": {"title": [{"text": {"content": title}}]},
                "시작일": {"date": {"start": start_date}},
                "종료일": {"date": {"start": end_date}},
                "상태": {"select": {"name": status}}
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def update_project(self, page_id, **kwargs):
        url = f"{self.base_url}/pages/{page_id}"
        properties = {}
        
        if "title" in kwargs:
            properties["이름"] = {"title": [{"text": {"content": kwargs["title"]}}]}
        if "start_date" in kwargs:
            properties["시작일"] = {"date": {"start": kwargs["start_date"]}}
        if "end_date" in kwargs:
            properties["종료일"] = {"date": {"start": kwargs["end_date"]}}
        if "status" in kwargs:
            properties["상태"] = {"select": {"name": kwargs["status"]}}

        data = {"properties": properties}
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json()

    def delete_project(self, page_id):
        url = f"{self.base_url}/pages/{page_id}"
        data = {"archived": True}
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json()