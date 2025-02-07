from sys import argv
from sample_generator import SampleGenerator

if __name__ == '__main__':
    generator = SampleGenerator(argv[1], "forward" if argv[2] == "forward" else "backward")
    try:
        generator.start_learning_loop()
    except KeyboardInterrupt:
        generator.session_stats.timer()
        print(generator.session_stats)
        input()
