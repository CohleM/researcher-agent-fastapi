from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta



ALLOWED_SCHEMAS = {"http", "https"}
ALLOWED_NETLOCK = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}

def _parse_video_id(url: str):
    """Parse a youtube url and return the video id if valid, otherwise None."""
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ALLOWED_SCHEMAS:
        return None

    if parsed_url.netloc not in ALLOWED_NETLOCK:
        return None

    path = parsed_url.path

    if path.endswith("/watch"):
        query = parsed_url.query
        parsed_query = parse_qs(query)
        if "v" in parsed_query:
            ids = parsed_query["v"]
            video_id = ids if isinstance(ids, str) else ids[0]
        else:
            return None
    else:
        path = parsed_url.path.lstrip("/")
        video_id = path.split("/")[-1]

    if len(video_id) != 11:  # Video IDs are 11 characters long
        return None

    return video_id





def format_time(seconds):
    # Convert seconds to timedelta object
    delta = timedelta(seconds=seconds)
    # Extract hours, minutes, and seconds
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Format the time as HH:MM:SS
    formatted_time = '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)
    return formatted_time

def combine_transcript(transcript):
    combined_transcript = []
    current_interval_start = transcript[0]['start']
    current_interval_text = ""

    for item in transcript:
        if item['start'] - current_interval_start > 900:  # Check if 5 minutes have passed
            duration = item['start'] - current_interval_start
            combined_transcript.append({
                'text': current_interval_text.strip(),
                'start': format_time(current_interval_start),
                'end': format_time(current_interval_start + duration),
                'duration': format_time(duration)
            })
            current_interval_start = item['start']
            current_interval_text = ""

        current_interval_text += item['text'] + " "

    # Append the remaining text as the last interval
    duration = transcript[-1]['start'] - current_interval_start
    combined_transcript.append({
        'text': current_interval_text.strip(),
        'start': format_time(current_interval_start),
        'end': format_time(current_interval_start + duration),
        'duration': format_time(duration)
    })

    return combined_transcript
