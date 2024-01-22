from lib import ensure_package_installed, install_packages, ensure_system_dependency_installed, install_3rd_party_dependencies

def download_youtube_video(url: str):
    """
    Context:
        This function can easily download an entire youtube video in the highest quality.

    Example:
        download_youtube_video("https://www.youtube.com/watch?v=9bZkp7q19f0")

    Output:
        Returns the filepath of the downloaded video.

    Reference:
        https://stackoverflow.com/questions/65802599/how-to-download-youtube-video-in-the-highest-quality-available

    Keywords:
        - youtube
        - download youtube video
        - download video
        - youtube video
        - youtube video downloader
        - youtube downloader
    """
    packages = ensure_package_installed(["pytube"], verbose=True)
    install_packages(packages, verbose=True)
    from pytube import YouTube

    # Downloading the YouTube Video
    print(f"[INFO] - Downloading YouTube Video from {url.split('?')[-1]}...")
    video_streams = YouTube(url)
    video = video_streams.streams.get_highest_resolution()
    video_filepath = video.download('/tmp/', max_retries=30)

    return video_filepath


def video2mp3(video_file, output_ext="mp3"):
    """
    Context:
        Converts any video file to an mp3 file.

    Example:
        video2mp3("video.mp4")

    Output:
        "/tmp/video.mp3"

    Reference:
        https://stackoverflow.com/questions/10058890/convert-mp4-to-mp3

    Keywords:
        - video to mp3
        - video2mp3
        - convert video to mp3
        - convert video2mp3
        - convert mp4 to mp3
        - convert mp4 to mp3 python
        - convert mp4 to mp3 ffmpeg
        - convert mp4 to mp3 linux
    """
    uninstalled_deps = ensure_system_dependency_installed(['ffmpeg'], verbose=True)
    install_3rd_party_dependencies(uninstalled_deps, verbose=True)

    import os
    import subprocess

    filename, ext = os.path.splitext(video_file)

    print(f"[INFO] - Converting {video_file} to {output_ext}...")
    output_filepath = f"/tmp/{filename}.{output_ext}"
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, output_filepath],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return output_filepath

