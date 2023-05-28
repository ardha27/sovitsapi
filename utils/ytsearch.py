from youtubesearchpython import VideosSearch

def ytsearch(search):

    videosSearch = VideosSearch(search, limit = 1)

    data = videosSearch.result()

    link = data['result'][0]['link']
    duration = data['result'][0]['duration']

    minutes, seconds = map(int, duration.split(':'))
    total_seconds = minutes * 60 + seconds

    return link, total_seconds

if __name__ == '__main__':
    ytsearch("idol yoasobi")