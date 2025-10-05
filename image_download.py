import concurrent.futures
import requests  

def downloadFiles(url, name):
    print(f"Start Downloading photo {name}")
    response = requests.get(url)
    open(f"photos/photo_{name}.jpg", "wb").write(response.content)
    print(f"Finish Downloading photo {name}")
    return "Done"

if __name__ == "__main__" :

    url = "https://picsum.photos/2000/3000"
    url_arg = [url for i in range(25)]
    name_arg = [i for i in range(1,26)]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(downloadFiles,url_arg,name_arg)
        for r in results:
            print(r)
