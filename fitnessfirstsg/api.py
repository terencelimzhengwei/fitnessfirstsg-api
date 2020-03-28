import requests
import json
import xmltodict

from fitnessfirstsg.error import (
    AuthenticationError, RequestsError, MissingCredentialsError
)

class FitnessFirstSG(object):
    def __init__(self, username, password):
        self.basepath = "https://api.fitnessmobileapps.com/api2/"
        self.authpath = "https://auth.mindbodyonline.com/issue/oauth2/token"
        self.mbopath = "https://api.mindbodyonline.com/0_5/"
        self.fitnessfirstid = 10966
        self.access_token = None
        self.username = username
        self.password = password
        if self.username and self.password:
            self.auth(username, password)

    def gym_list(self):
        url = "{}all_gym/{}".format(self.basepath, self.fitnessfirstid)
        return self._get(url)

    def gym_info(self, gym_id=20850):
        url = "{}gym/{}".format(self.basepath, gym_id)
        return self._get(url)

    def auth(self, username=None, password=None):
        if username and password:
            response = self._get_auth_token(username, password)
            self.username = username
            self.password = password
        elif self.username and self.password:
            response = self._get_auth_token(self.username, self.password)
        else:
            raise MissingCredentialsError
        if "access_token" in response:
            self.access_token = response["access_token"]
            print("Authenticated successfully")
        else:
            raise AuthenticationError

    def user_details(self):
        url = "{}ClientService.asmx".format(self.mbopath)
        request_type = "GetClients"
        attributes = ('')

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def user_schedule(self):
        url = "{}ClientService.asmx".format(self.mbopath)
        request_type = "GetClientSchedule"
        attributes = ('')

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def gym_locations(self):
        url = "{}SiteService.asmx".format(self.mbopath)
        request_type = "GetLocations"
        attributes = ('')

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def classes(self, start_date, end_date,
                gym_id, hide_cancelled_classes='true'):
        url = "{}ClassService.asmx".format(self.mbopath)
        request_type = "GetClasses"
        attributes = ('<LocationIDs><int>{0}</int></LocationIDs>'
                      '<ProgramIDs>'
                      '<int>22</int><int>23</int><int>24</int><int>25</int>'
                      '</ProgramIDs>'
                      '<StartDateTime>{1}</StartDateTime>'
                      '<EndDateTime>{2}</EndDateTime>'
                      '<HideCanceledClasses>{3}</HideCanceledClasses>'
                      '<Fields><string>Classes.Resource</string></Fields>'
                      ).format(gym_id, start_date,
                               end_date, hide_cancelled_classes)

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def programs(self):
        url = "{}SiteService.asmx".format(self.mbopath)
        request_type = "GetPrograms"
        attributes = ('<ScheduleType>All</ScheduleType>'
                      '<OnlineOnly>true</OnlineOnly>')

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def book_class(self, class_id, require_payment='false',
                   waitlist='false', send_email='true'):
        url = "{}ClassService.asmx".format(self.mbopath)
        request_type = "GetClasses"
        attributes = ('<ClassIDs><int>{}</int></ClassIDs>'
                      '<RequirePayment>{}</RequirePayment>'
                      '<Waitlist>{}</Waitlist>'
                      '<SendEmail>{}</SendEmail>'
                      ).format(class_id, require_payment,
                               waitlist, send_email)

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def cancel_class(self, class_id, send_email='true', late_cancel='false'):
        url = "{}ClassService.asmx".format(self.mbopath)
        request_type = "RemoveClientsFromClasses"
        attributes = ('<ClassIDs><int>{}</int></ClassIDs>'
                      '<SendEmail>{}</SendEmail>'
                      '<LateCancel>{}</LateCancel>'
                      ).format(class_id, send_email, late_cancel)

        data = self._gen_xml(request_type, attributes)
        return self._soap_post(url, request_type, data)

    def _get_auth_token(self, username, password):
        url = self.authpath

        headers = {
            "Authorization": "Basic YW5kcm9pZGVuZ2FnZTplbmdhZ2VfdXNlcg==",
            "Content-Type": "application/json",
        }
        data = {
            "SubscriberId": "741470",
            "grant_type": "password",
            "password": password,
            "scope": "urn:mboframeworkapi",
            "username": username
        }
        if username == "api_user":
            data.pop('SubscriberId', None)

        return self._post(url, headers, json.dumps(data))

    @staticmethod
    def _get(url, headers=None, data=None):
        response = requests.get(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError
        else:
            raise RequestsError(response.status_code)

    @staticmethod
    def _post(url, headers=None, data=None):
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError
        else:
            raise RequestsError(response.status_code)

    def _soap_post(self, url, request_type, data=None):
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'SOAPAction': ("http://clients.mindbodyonline.com/api/0_5/{}"
                           .format(request_type)),
            'Content-Type': 'text/xml; charset=utf-8'
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return self._parse_xml(response.content)
        elif response.status_code == 401:
            raise AuthenticationError
        else:
            print(response.text)
            raise RequestsError(response.status_code)

    @staticmethod
    def _gen_xml(request_type, attributes):
        formatted_xml = ('<soapenv:Envelope xmlns:soapenv='
                         '"http://schemas.xmlsoap.org/soap/envelope/" '
                         'xmlns="http://clients.mindbodyonline.com/api/0_5">'
                         '<soapenv:Header/>'
                         '<soapenv:Body>'
                         '<{0} xmlns="http://clients.mindbodyonline.com/api/0_5">'
                         '<Request>'
                         '<SourceCredentials>'
                         '<SiteIDs><int>741470</int></SiteIDs>'
                         '</SourceCredentials>'
                         '<XMLDetail>Full</XMLDetail>{1}</Request></{0}>'
                         '</soapenv:Body>'
                         '</soapenv:Envelope>').format(request_type, attributes)
        return formatted_xml

    @staticmethod
    def _parse_xml(body):
        return json.loads(json.dumps(xmltodict.parse(body)))
