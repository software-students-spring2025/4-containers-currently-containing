from webcam_streamer import app

def test_video_feed_route():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        chunk = next(response.response, None)
        assert chunk is not None
        assert b'--frame' in chunk
