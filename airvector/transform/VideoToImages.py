import os
import cv2


def video_to_images(file_path: str, interval: int = 2):
    cap = cv2.VideoCapture(file_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate of the video
    frame_interval = int(
        interval * frame_rate
    )  # Calculate the frame interval based on the time interval

    frame_count = 0
    saved_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_path = os.path.join(
                os.path.dirname(file_path), f"frame_{frame_count}.jpeg"
            )
            cv2.imwrite(frame_path, frame)
            saved_frames.append((frame_count, frame_path))

        frame_count += 1

    cap.release()
    return saved_frames
