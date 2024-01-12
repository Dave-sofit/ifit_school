from json import dumps
from datetime import datetime
from typing import Any

from httpx import AsyncClient, RequestError, Response

from bot.common.enums import RequestTypes
from bot.config import settings
from bot.serviceObjects.users import UserOut
from bot.serviceObjects.courses import CourseOut


async def send(base_url: str, url: str = '', requestType: RequestTypes = RequestTypes.GET, headers: dict = None,
               params: dict = None, dataDict: dict = None) -> Response:
    async with AsyncClient(base_url=base_url, headers=headers) as client:
        try:
            if requestType == RequestTypes.GET:
                response = await client.get(url=url, params=params)
            elif requestType == RequestTypes.POST:
                response = await client.post(url=url, params=params, json=dataDict)
            elif requestType == RequestTypes.HEAD:
                response = await client.post(url=url, params=params)
            elif requestType == RequestTypes.PUT:
                response = await client.put(url=url, params=params, json=dataDict)
            elif requestType == RequestTypes.HEAD:
                response = await client.post(url=url, params=params)
            else:
                response = Response(status_code=400, text=dumps({'error': 'bad request type'}))

        except RequestError as exc:
            response = Response(status_code=500, text=dumps({'error': exc.args[0]}))

    return response


class Order:
    def __init__(self, user: UserOut, course: CourseOut, startDate: datetime):
        self.user = user
        self.course = course
        self.startDate = startDate


class Sender:
    @classmethod
    async def sendToCrm(cls, obj: Any):
        pass


class SenderOrder(Sender):
    @classmethod
    async def sendToCrm(cls, obj: Order):
        product = {'id': obj.course.crmId}
        products = [product]

        headers = {'Content-Type': 'application/json'}

        data = {'form': settings.CRM_TOKEN, 'organizationId': '1', 'getResultData': '0', 'comment': 'from bot'}
        data.update(products=products)
        data.update(fName=obj.user.firstName, lName=obj.user.lastName)
        data.update(phone=f'+{obj.user.phone}')
        data.update(startKursu=obj.startDate.strftime('%d.%m.%Y'))

        return await send(base_url=settings.CRM_URL, url=f'/handler/', requestType=RequestTypes.POST,
                          headers=headers, dataDict=data)
