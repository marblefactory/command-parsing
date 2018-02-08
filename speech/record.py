import queue
import sounddevice as sd
import soundfile as sf


class Recorder:
    """
    Used to record and save audio.
    """

    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        # Contains frames of recorded audio.
        self.recorded_queue = queue.Queue()

    def callback(self, in_data, frames, time, status):
        if status:
            print('STATUS', status)

        self.recorded_queue.put(in_data.copy())

    def record(self):
        """
        A blocking call to record audio, until the enter key is pressed. This stores the audio internally. `write`
        can be used to save the recording.
        """
        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.callback):
             input('Press Enter to stop\n')

    def write(self, file_name: str):
        """
        Writes any recorded audio to the specified file.
        """
        with sf.SoundFile(file_name, mode='w', samplerate=self.sample_rate, channels=1) as file:
            while not self.recorded_queue.empty():
                file.write(self.recorded_queue.get())
