from flask import Flask, request, jsonify
import yt_dlp
import urllib.request
import json

app = Flask(__name__)

def get_stream_from_proxies(video_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. Piped Engine (Fastest & blocks bypass)
    piped_instances = [
        f"https://api.piped.private.coffee/streams/{video_id}",
        f"https://pipedapi.tokhmi.xyz/streams/{video_id}",
        f"https://pipedapi.kavin.rocks/streams/{video_id}"
    ]
    for p_url in piped_instances:
        try:
            req = urllib.request.Request(p_url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    title = data.get('title', 'Video')
                    streams = data.get('videoStreams', [])
                    for s in streams:
                        if not s.get('videoOnly', True) and s.get('format', '').lower() == 'mp4':
                            return s.get('url'), title
                    for s in streams:
                        if not s.get('videoOnly', True) and s.get('url'):
                            return s.get('url'), title
        except Exception:
            continue

    # 2. Invidious Fallback Engine
    invidious_instances = [
        f"https://invidious.nerdvpn.de/api/v1/videos/{video_id}",
        f"https://inv.nadeko.net/api/v1/videos/{video_id}",
        f"https://invidious.jing.rocks/api/v1/videos/{video_id}",
        f"https://inv.tux.pizza/api/v1/videos/{video_id}"
    ]
    for inv_url in invidious_instances:
        try:
            req = urllib.request.Request(inv_url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    title = data.get('title', 'Video')
                    formats = data.get('formatStreams', [])
                    for f in formats:
                        if f.get('container') == 'mp4' or 'video/mp4' in f.get('type', ''):
                            return f.get('url'), title
                    if formats and formats[0].get('url'):
                        return formats[0].get('url'), title
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
                'player_client': ['android', 'ios', 'mweb']
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

    # 1. High-Speed Bypass Proxy Engines
    stream_url, title = get_stream_from_proxies(video_id)
    if stream_url:
        return jsonify({'success': True, 'title': title, 'stream_url': stream_url})

    # 2. Native yt-dlp Engine
    try:
        stream_url, title = get_stream_from_ytdlp(video_id)
        if stream_url:
            return jsonify({'success': True, 'title': title, 'stream_url': stream_url})
    except Exception:
        pass

    return jsonify({'success': False, 'error': 'Stream extraction failed'}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Server Live'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
