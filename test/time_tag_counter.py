# Check time duration
# Save duration with tag


import time

class time_tag_counter:
    def __init__(self):
        self.time_tag = dict()

    # Make Start point
    def start(self, tag:str):
        if tag not in self.time_tag:
            self.time_tag[tag] = []
        self.time_tag[tag].append(time.time())

    # Calculate Duration from start point
    def stop(self, tag:str):
        self.time_tag[tag][-1] = time.time() - self.time_tag[tag][-1]
        if self.time_tag[tag][-1] < 0:
            raise ValueError(f"tag({tag}) is not started or started twice")
        return self.time_tag[tag]

if __name__ == "__main__":
    counter = time_tag_counter()
    counter.start("1")
    counter.start("3")
    time.sleep(1)
    counter.stop("1")
    counter.start("1")
    counter.start("2")
    time.sleep(1)
    counter.stop("1")
    counter.stop("2")
    counter.stop("3")
    print(counter.time_tag)
