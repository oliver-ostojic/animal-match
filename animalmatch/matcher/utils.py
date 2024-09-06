import requests


def fetch_image_url_from_api(name):
    api_url = 'https://api.unsplash.com/search/photos'
    param = {
        'query': name,
        'orientation': 'landscape',
        'client_id': 'ndp6N_YeWDj_MssjTVUMY5br6BPJHdnKbJA6myw3SW4'
    }
    response = requests.get(api_url, params=param)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][3]['urls']['regular']
        else:
            return None
    else:
        raise ValueError("Animal image URL could not be fetched")


def fetch_animal_data_from_api(name):
    api_url = 'https://api.api-ninjas.com/v1/animals?name={}'.format(name)
    headers = {'X-Api-Key': '82RGeV546Un8+rn0uaQGVA==1EbbcqODn6PzL7qx'}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif not response.json() or len(response.json()) == 0:
        raise ValueError("No animals found, invalid search.")
    else:
        raise ValueError(response.text)
