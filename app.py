from flask import Flask, request, jsonify
import yt_dlp
import urllib.request
import json

app = Flask(__name__)

INVIDIOUS_INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.nerdvpn.de",
    "https://yt.artemislena.eu",
    "https://invidious.drgns.space"
]

def get_stream_from_invidious(video_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    for base_url in INVIDIOUS_INSTANCES:
        try:
            url = f"{base_url}/api/v1/videos/{video_id}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    formats = data.get('formatStreams', [])
                    for f in formats:
                        if f.get('container') == 'mp4' or 'video/mp4' in f.get('type', ''):
                            return f.get('url'), data.get('title', 'Video')
                    if formats:
                        return formats[0].get('url'), data.get('title', 'Video')
        except Exception:
            continue
    return None, None

def get_stream_from_ytdlp(video_id):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get('url'), info.get('title', 'Video')

@app.route('/stream', methods=['GET'])
def get_stream_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'success': False, 'error': 'ID missing'}), 400

    # 1. Fast & Unblocked Invidious Engine
    stream_url, title = get_stream_from_invidious(video_id)
    if stream_url:
        return jsonify({'success': True, 'title': title, 'stream_url': stream_url})

    # 2. yt-dlp iOS Fallback
    try:
        stream_url, title = get_stream_from_ytdlp(video_id)
        if stream_url:
            return jsonify({'success': True, 'title': title, 'stream_url': stream_url})
    except Exception as e:
        pass

    return jsonify({'success': False, 'error': 'Stream extraction failed'}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Server Live'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
