from googleapiclient.discovery import build

YOUTUBE_API_KEY = "AIzaSyC3d7jZJmVi1a-RgXg8h7b_Ru1TFFpf1K8"

def youtubevd(query, max_results=6, default=["plant diseases", "penyakit tanaman"]):

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search_vd = query if query else default[0]
    
    response = youtube.search().list(
        q=search_vd,
        part='snippet',
        maxResults=max_results,
        type='video'
    ).execute()
    
    videos = [] 
    for item in response['items']:
        video = {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'thumbnail': item['snippet']['thumbnails']['default']['url'],
            'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        videos.append(video)
    
    if not videos and query:
        # Jika tidak ada hasil untuk penyakit tanaman, cari video terkait jenis tanaman
        response = youtube.search().list(
            q=default,
            part='snippet',
            maxResults=max_results,
            type='video'
        ).execute()
        
        for item in response['items']:
            video = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video)
    
    return videos
