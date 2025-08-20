from abc import ABC
from datetime import date
import json
import requests
import aiohttp
import urllib

class RequestResult(ABC):
    status_code: int
    errors: str | None
    
class PostResult(RequestResult):
    pass

class NavigateItem:
    name: str
    is_file: bool

class NavigateResult(RequestResult):
    data: list[NavigateItem] | None
    
class DownloadResult(RequestResult):
    data: bytearray | None
    mime_type: str

class HttpClient:
    __host: str
    __apikey: str | None
    __apiversion: str | None
    
    
    def __init__(self, host: str, apikey: str | None, apiversion: str | None):
        if host is None or host.__len__() == 0:
            raise ValueError("host")
        
        self.__host = host
        self.__apikey = apikey
        self.__apiversion = apiversion
        
        if self.__apiversion is None or self.__apiversion.strip() == "":
            self.__apiversion = "v1"
            
    def __create_backup_url(self) -> str:
        url = self.__host + f"/api/{self.__apiversion}/backup"
        return url
    
    def __create_navigate_url(self, path: str | None) -> str:
        url = self.__host + f"/api/{self.__apiversion}/backup/"
        if path is not None:
            splitted = path.split("/")
            for s in splitted:
                url = url + urllib.parse.quote(s) + "/"
        
        return url
    
    def __create_download_url(self, path: str) -> str:
        url = self.__host + f"/api/{self.__apiversion}/file/"
        if path is not None:
            splitted = path.split("/")
            for s in splitted:
                url = url + urllib.parse.quote(s) + "/"
        
        return url
    def Backup(self, loggerTypeCode: str, loggerSerial: str, timestamp: date, file: str) -> PostResult:
        url = self.__create_backup_url()
        response = None
        result = None
        with open(file, "rb") as f:
            body = { "loggerTypeCode": loggerTypeCode, "loggerSerial": loggerSerial, "timestamp": timestamp }
            files = { "file": f}
            response = requests.post(url, data = body, files=files, headers={"X-API-Key":self.__apikey})
        
            
        result = RequestResult()
        result.status_code = response.status_code
        if not response.ok:
            result.errors = response.json()
        else:
            result.errors = None
        
        return result
    
    async def BackupAsync(self, loggerTypeCode: str, loggerSerial: str, timestamp: date, file: str) -> PostResult:
        url = self.__create_backup_url()
        response = None
        result = None
        async with aiohttp.ClientSession(headers={"X-API-Key":self.__apikey}) as session:
            with open(file, 'rb') as f:
                body = { "loggerTypeCode": loggerTypeCode, 
                        "loggerSerial": loggerSerial, 
                        "timestamp": timestamp, 
                        "file": f
                        }
                async with session.post(url, data=body,) as response:
                    result = RequestResult()
                    result.status_code = response.status
                    if not response.ok:
                        result.errors = await response.json()
                    else:
                        result.errors = None
                    
        return result
    
    def Navigate(self, path: str | None = None) -> NavigateResult:
        url = self.__create_navigate_url(path)
        response = None
        result = NavigateResult()
        
        response = requests.get(url, headers={"X-API-Key":self.__apikey})
        
        result.status_code = response.status_code
        
        if response.ok:
            data = []

            for d in response.json():
                item = NavigateItem()
                item.name = d["name"]
                item.is_file = d["isfile"]
                data.append(item)
            
            result.data = data
            result.errors = None
        else:
            result.errors = response.json()
            result.data = None
        
        return result
    
    def Download(self, path: str) -> DownloadResult:
        url = self.__create_download_url(path)
        response = None
        result = DownloadResult()
        
        response = requests.get(url, headers={"X-API-Key":self.__apikey})
                
        result.status_code = response.status_code
        
        if response.ok:
            result.data = response.content
            result.mime_type = response.headers["content-type"]
            result.errors = None
        else:
            result.errors = response.json()
            result.data = None
            result.mime_type = None
        
        return result