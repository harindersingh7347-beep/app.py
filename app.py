from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/stream', methods=['GET'])
def get_stream_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'success': False, 'error': 'ID missing'}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'Video')
            return jsonify({'success': True, 'title': title, 'stream_url': stream_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Server Live'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
