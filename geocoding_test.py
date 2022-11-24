import json

import pytest
import requests

from DataCreator import DataCreator
from DataReader import DataReader


@pytest.fixture(scope="class")
def prepare_test_data():
    DataCreator.create_full_information_sheet("full_data.xlsx")
    DataCreator.create_queries_sheet("queries.xlsx")
    DataCreator.create_landmarks_sheet("landmarks.xlsx")


class TestGeocoding:
    direct_geocoding_url = "https://nominatim.openstreetmap.org/search?"
    reverse_geocoding_url = "https://nominatim.openstreetmap.org/reverse?"

    @pytest.mark.parametrize('data', DataReader.generate_full_data("full_data.xlsx"))
    def test_direct_geocoding_with_parameters(self, data):
        """
        Метод, отправляющий запрос со всеми параметрами объекта и сравнивающий полученные координаты с ожидаемыми
        :param data: словарь, содержащий полную информацию об адресе объекта
        :return: проверяет разницу между ожидаемыми координатами и действительными
        """
        params = {
            'street': data['address']['house_number'] + ' ' + data['address']['road'],
            'city': data['address']['city'],
            'county': data['address']['suburb'],
            'state': data['address']['state'],
            'country': data['address']['country'],
            'postalcode': data['address']['postcode'],
            'format': 'json'
        }
        response = requests.get(self.direct_geocoding_url, params)
        ans = json.loads(response.text)

        expected_lat = float(data['lat'])
        expected_lon = float(data['lon'])
        actual_lat = float(ans[0]['lat'])
        actual_lon = float(ans[0]['lon'])

        assert all([abs(round(expected_lat, 4) - round(actual_lat, 4)) < 0.0001,
                    abs(round(expected_lon, 4) - round(actual_lon, 4)) < 0.0001]), \
            "Разница в координатах превышает допустимую"

    @pytest.mark.parametrize('data', DataReader.generate_query_data('queries.xlsx'))
    def test_direct_geocoding_with_queries(self, data):
        """
        Метод, отправляющий запрос с произвольным названием объекта и сравнивающий полученные координаты с ожидаемыми
        :param data: словарь, содержащий текст запроса и ожидаемые координаты
        :return: проверяет разницу между ожидаемыми координатами и действительными
        """
        params = {
            'q': data['q'],
            'format': 'json'
        }
        response = requests.get(self.direct_geocoding_url, params)
        response_data = json.loads(response.text)

        expected_lat = float(data['lat'])
        expected_lon = float(data['lon'])
        actual_lat = float(response_data[0]['lat'])
        actual_lon = float(response_data[0]['lon'])

        assert abs(round(expected_lat, 4) - round(actual_lat, 4)) < 1 and \
               abs(round(expected_lon, 4) - round(actual_lon, 4)) < 1, "Разница в координатах превышает допустимую"

    @pytest.mark.parametrize('data', DataReader.generate_query_data('landmarks.xlsx'))
    def test_status_code_of_direct_geocoding_with_queries(self, data):
        """
        Метод, отправляющий корректный запрос с произвольным описанием объекта и проверяющий статус код ответа
        :param data: словарь, содержащий текст запроса и ожидаемые координаты
        :return: проверяет статус код
        """
        params = {
            'q': data['q'],
            'format': 'json'
        }
        response = requests.get(self.direct_geocoding_url, params)
        assert response.status_code == 200, "Получен неверный код ответа"

    @pytest.mark.parametrize('query', DataReader.generate_incorrect_query(5))
    def test_status_code_of_direct_geocoding_of_incorrect_query(self, query):
        """
        Метод, отправляющий случайно сгенерированный запрос (подразумевается, что он некорректен) и проверяющий, удалось
        ли серверу найти объект
        :param query: случайно сгенерированный текст запроса
        :return: проверяет наличие в ответе данных об объекте
        """
        params = {
            'q': query,
            'format': 'json'
        }
        response = requests.get(self.direct_geocoding_url, params)
        assert not json.loads(response.text), "Запрос был корректно обработан"

    @pytest.mark.parametrize('data', DataReader.generate_full_data("full_data.xlsx"))
    def test_status_code_of_direct_geocoding_with_parameters(self, data):
        """
        Метод, отправляющий корректное полное описание объекта и проверяющий статус код ответа
        :param data: словарь с полным описанием объекта
        :return: проверяет статус код
        """
        params = {
            'street': data['address']['house_number'] + ' ' + data['address']['road'],
            'city': data['address']['city'],
            'county': data['address']['suburb'],
            'state': data['address']['state'],
            'country': data['address']['country'],
            'postalcode': data['address']['postcode'],
            'format': 'json'
        }
        response = requests.get(self.direct_geocoding_url, params)
        assert response.status_code == 200, "Получен неверный код ответа"

    @pytest.mark.parametrize("data", DataReader.generate_query_data("landmarks.xlsx"))
    def test_status_code_of_reverse_geocoding_with_queries(self, data):
        """
        Метод, отправляющий произвольные корректные координаты объекта и проверяющий статус код ответа
        :param data: словарь, содержащий произвольное описание объекта
        :return: проверяет статус код
        """
        params = {
            'lat': data['lat'],
            'lon': data['lon'],
            'format': 'json'
        }
        response = requests.get(self.reverse_geocoding_url, params)
        assert response.status_code == 200, "Получен неверный код ответа"

    @pytest.mark.parametrize('data', DataReader.generate_full_data('full_data.xlsx'))
    def test_reverse_geocoding_with_full_data(self, data):
        """
        Метод, отправляющий координаты объекта и сравнивающий полную информацию об объекте
        :param data: словарь, содержащий полную информацию об объекте
        :return: проверяет, все ли поля совпадают
        """
        params = {
            'lat': data['lat'],
            'lon': data['lon'],
            'format': 'json'
        }
        response = requests.get(self.reverse_geocoding_url, params)
        resp_json = json.loads(response.text)
        assert all(data['address'][key] == resp_json['address'][key] for key in data['address'].keys()), \
            "Полученные значения полей не совпадают с ожидаемыми"

    """
    Изначально ожидалось, что в следующей паре методов код ответа сервера будет 400, но запрос корректно обрабатывается
    Вместо этого сервер посылает код ответа 200, но в сообщении пишет о том, что распознать координату у него не вышло
    """

    @pytest.mark.parametrize('lat, lon', DataReader.generate_incorrect_lats(5))
    def test_reverse_geocoding_with_incorrect_lats(self, lat, lon):
        """
        Метод, проверяющий, сможет ли сервер обработать некорректный запрос
        :param lat: неверное значение долготы
        :param lon: корректное значение широты
        :return: проверяет, удалось ли серверу обработать запрос
        """
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        response = requests.get(self.reverse_geocoding_url, params)
        assert 'error' in json.loads(response.text), "Запрос был корректно обработан"

    @pytest.mark.parametrize('lat, lon', DataReader.generate_incorrect_lons(5))
    def test_reverse_geocoding_with_incorrect_lons(self, lat, lon):
        """
        Метод, проверяющий, сможет ли сервер обработать некорректный запрос
        :param lat: корректное значение долготы
        :param lon: неверное значение широты
        :return: проверяет, удалось ли серверу обработать запрос
        """
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json'
        }
        response = requests.get(self.reverse_geocoding_url, params)
        assert 'error' in json.loads(response.text), "Запрос был корректно обработан"


if __name__ == '__main__':
    pytest.main()
