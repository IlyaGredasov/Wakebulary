from args_parser import parse_args
from src.backend.sample_generator import SampleGenerator

if __name__ == '__main__':
    args = parse_args()
    generator = SampleGenerator(args.mode, args.alpha, args.clear_delay)
    try:
        generator.start_learning_loop(args.sample_size, args.randomness_const)
    except KeyboardInterrupt:
        generator.session_stats.timer()
        print(generator.session_stats)
        input()
