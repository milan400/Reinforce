import os
import subprocess
import regex as re
import time
import matplotlib.pyplot as plt
from IPython import display as ipythondisplay


def extract_song_snippet(generated_text):
    pattern = '\n\n(.*?)\n\n'
    search_results = re.findall(pattern, generated_text, overlapped=True, flags=re.DOTALL)
    songs = [song for song in search_results]
    print ("Found {} possible songs in generated texts".format(len(songs)))
    return songs

def save_song_to_abc(song, filename="tmp"):
    save_name = "{}.abc".format(filename)
    with open(save_name, "w") as f:
        f.write(song)
    return filename

def abc2wav(abc_file):
    path_to_tool = '/home/krdevkota/Desktop/May25/sound_generation/abc2wav'
    cmd = "{} {}".format(path_to_tool, abc_file)
    return os.system(cmd)

def play_wav(wav_file):
    from IPython.display import Audio
    return Audio(wav_file)

def play_generated_song(generated_text):
    songs = extract_song_snippet(generated_text)
    if len(songs) == 0:
        print ("No valid songs found in generated text. Try training the model longer or increasing the amount of generated music to ensure complete songs are generated!")

    for song in songs:
        basename = save_song_to_abc(song)
        ret = abc2wav(basename+'.abc')
        if ret == 0: #did not suceed
            return play_wav(basename+'.wav')
    print ("None of the songs were valid, try training longer to improve syntax.")


def custom_progress_text(message):
    import progressbar
    from string import Formatter

    message_ = message.replace('(', '{')
    message_ = message_.replace(')', '}')

    keys = [key[1] for key in Formatter().parse(message_)]

    ids = {}
    for key in keys:
        if key is not None:
            ids[key] = float('nan')

    msg = progressbar.FormatCustomText(message, ids)
    return msg

def create_progress_bar(text=None):
    import progressbar
    if text is None:
        text = progressbar.FormatCustomText('')
    bar = progressbar.ProgressBar(widgets=[
        progressbar.Percentage(),
        progressbar.Bar(),
        progressbar.AdaptiveETA(), '  ',
        text,
    ])
    return bar

class PeriodicPlotter:
    def __init__(self, sec, xlabel='', ylabel='', scale=None):
        from IPython import display as ipythondisplay
        import matplotlib.pyplot as plt
        import time

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.sec = sec
        self.scale = scale

        self.tic = time.time()

    def plot(self, data):
        if time.time() - self.tic > self.sec:
            plt.cla()
      
            if self.scale is None:
                plt.plot(data)
            elif self.scale == 'semilogx':
                plt.semilogx(data)
            elif self.scale == 'semilogy':
                plt.semilogy(data)
            elif self.scale == 'loglog':
                plt.loglog(data)
            else:
                raise ValueError("unrecognized parameter scale {}".format(self.scale))

            plt.xlabel(self.xlabel); plt.ylabel(self.ylabel)
            ipythondisplay.clear_output(wait=True)
            ipythondisplay.display(plt.gcf())

            self.tic = time.time()


class LossHistory:
    def __init__(self, smoothing_factor=0.0):
        self.alpha = smoothing_factor
        self.loss = []
    def append(self, value):
        self.loss.append( self.alpha*self.loss[-1] + (1-self.alpha)*value if len(self.loss)>0 else value )
    def get(self):
        return self.loss
