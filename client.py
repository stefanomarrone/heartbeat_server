import time
import requests


def main():
    url = "http://localhost:4415/getbeat"

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"Heartbeat ricevuto: {data['beat']}")
            else:
                print(f"Errore nella risposta: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta: {e}")

        time.sleep(10)


if __name__ == "__main__":
    main()