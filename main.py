from src.backend.sample_generator import SampleGenerator

if __name__ == '__main__':
    generator = SampleGenerator("eng")
    try:
        generator.start_learning_loop()
    except KeyboardInterrupt:
        generator.session_stats.timer()
        print(generator.session_stats)
