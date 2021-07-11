import requests


def test_get_ressources_usage():
    response = requests.get("http://127.0.0.1:8000/ressources-usage/")
    print(response)
    print("------------------")

    json_response = response.json()
    for elem in json_response:
        print(elem)


test_get_ressources_usage()
