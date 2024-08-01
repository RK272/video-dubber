import tkinter as tk
from tkinter import filedialog
import cv2
import pyaudio
import wave
import threading
from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image, ImageTk


class AudioDubbingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Dubbing App")

        self.video_file = ""
        self.audio_file = "recorded_audio.wav"
        self.is_recording = False
        self.is_playing = True

        self.load_button = tk.Button(root, text="Load Video", command=self.load_video)
        self.load_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Playback", command=self.play_video)
        self.start_button.pack(pady=10)

    def load_video(self):
        self.video_file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
        print(f"Loaded video file: {self.video_file}")

    def play_video(self):
        if self.video_file:
            self.video_window = tk.Toplevel(self.root)
            self.video_window.title("Video Playback")

            self.canvas = tk.Canvas(self.video_window, width=900, height=600)
            self.canvas.pack()

            controls_frame = tk.Frame(self.video_window)
            controls_frame.pack()

            self.play_button = tk.Button(controls_frame, text="Play", command=self.start_playback)
            self.play_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.pause_button = tk.Button(controls_frame, text="Pause", command=self.pause_playback)
            self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.record_button = tk.Button(controls_frame, text="Start Recording", command=self.start_recording)
            self.record_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.stop_record_button = tk.Button(controls_frame, text="Stop Recording", command=self.stop_recording)
            self.stop_record_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.merge_button = tk.Button(controls_frame, text="Merge Audio with Video", command=self.merge_audio_video)
            self.merge_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.save_button = tk.Button(controls_frame, text="Save Merged Video", command=self.save_video)
            self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

            self.playback_thread = threading.Thread(target=self._play_video)
            self.playback_thread.start()

    def start_playback(self):
        self.is_playing = True

    def pause_playback(self):
        self.is_playing = False

    def _play_video(self):
        cap = cv2.VideoCapture(self.video_file)
        while cap.isOpened():
            if self.is_playing:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (900, 600))
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.update_idletasks()

                # This keeps the reference to avoid garbage collection
                self.canvas.imgtk = imgtk

            self.root.update()

        cap.release()

    def start_recording(self):
        self.is_recording = True
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()
        print("Started recording audio...")

    def stop_recording(self):
        self.is_recording = False
        self.audio_thread.join()
        print("Stopped recording audio.")

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = []
        while self.is_recording:
            data = stream.read(1024)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(self.audio_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    def merge_audio_video(self):
        if self.video_file and self.audio_file:
            self.video_clip = VideoFileClip(self.video_file)
            self.audio_clip = AudioFileClip(self.audio_file)
            self.final_clip = self.video_clip.set_audio(self.audio_clip)
            print("Merged audio with video.")

    def save_video(self):
        if self.final_clip:
            self.final_clip.write_videofile("output_video.mp4", codec="libx264")
            print("Saved merged video as output_video.mp4")


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioDubbingApp(root)
    root.mainloop()
