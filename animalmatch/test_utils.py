import pytest

from matcher.models import Animal
from matcher.utils import fetch_animal_data_from_api, fetch_image_url_from_api


@pytest.mark.parametrize(
    "name, expected_result", [
        ("tiger", True),
        ("Tiger", True),
        ("turtle", True),
        ("truck", False),
        (" ", False),
        ("", False),
        ("human", False)
    ]
)
@pytest.mark.utils
def test_fetch_animal_data_from_api(mocker, name, expected_result):
    mock_response = mocker.patch("matcher.utils.requests.get")
    if expected_result:
        mock_response.return_value.status_code = 200
        mock_response.return_value.json.return_value = {
            "name": name, "taxonomy": "ex_taxonomy", "locations": "ex_locations"
        }
        data = fetch_animal_data_from_api(name)
        assert isinstance(data, dict)
        assert data["name"].lower() == name.lower()
    else:
        mock_response.return_value.status_code = 400
        with pytest.raises(ValueError):
            fetch_animal_data_from_api(name)


@pytest.mark.parametrize(
    "name, expected_result", [
        ("tiger", True),
        ("Tiger", True),
        ("turtle", True),
        ("truck", True),
        ("excitement", True),
        (" ", False),
        ("", False)
    ]
)
# In using 'mock' we are replacing the request.get() for the API in the real code just for testing
# No network calls should be made in testing
@pytest.mark.utils
def test_fetch_image_url_from_api(mocker, name, expected_result):
    mock_response = mocker.patch("matcher.utils.requests.get")
    if expected_result:
        mock_response.return_value.status_code = 200
        mock_response.return_value.json.return_value = {
            'results': [{'urls': {'regular': 'https://example.com/image.jpg'}}]
        }
        url = fetch_image_url_from_api(name)
        assert isinstance(url, str) and len(url) > 0
    else:
        mock_response.return_value.status_code = 400
        with pytest.raises(ValueError):
            fetch_image_url_from_api(name)
