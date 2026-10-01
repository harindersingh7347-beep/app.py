from flask import Flask, request, jsonify
import yt_dlp
import urllib.request
import json

app = Flask(__name__)

def get_stream_fallback(video_id):
    instances = [
        f"https://inv.nadeko.net/api/v1/videos/{video_id}",
        f"https://invidious.nerdvpn.de/api/v1/videos/{video_id}",
        f"https://yt.artemislena.eu/api/v1/videos/{video_id}"
    ]
    for url in instances:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    for fmt in data.get('formatStreams', []):
                        if fmt.get('url'):
                            return fmt['url']
        except Exception:
            continue
    return None

@app.route('/stream', methods=['GET'])
def get_stream_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'success': False, 'error': 'ID missing'}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # iOS innertube client YouTube bot detection bypass karta hai
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'mweb']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'Video')
            if stream_url:
                return jsonify({'success': True, 'title': title, 'stream_url': stream_url})
    except Exception as e:
        print("yt-dlp error:", str(e))

    fallback_url = get_stream_fallback(video_id)
    if fallback_url:
        return jsonify({'success': True, 'title': 'Video', 'stream_url': fallback_url})

    return jsonify({'success': False, 'error': 'Stream fetch failed'}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Server Live'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
