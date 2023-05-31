import sys
import cv2
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

def find_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())

    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)

    return scene_manager.get_scene_list(video_manager.get_base_timecode())

# if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python scene_detection.py <video_path>")
    #     sys.exit(1)

video_path = r"C:\Users\Rafay\Sample Data 2\sample.mp4"
scenes = find_scenes(video_path)

print("Scenes:")
for start, end in scenes:
    print(f"Start: {start.get_seconds()}, End: {end.get_seconds()}")