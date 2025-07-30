from datetime import date
import http.client as cl
import requests

class RequestResult:
    status_code: int
    errors: str | None

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
    
    def Backup(self, loggerTypeCode: str, loggerSerial: str, timestamp: date, file: str) -> RequestResult:
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
        
        return result
        