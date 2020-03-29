import os

import neat

from nn_player import NeuralNetMaster


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(False))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    # pop.add_reporter(neat.Checkpointer(10, filename_prefix="first-"))

    winner = pop.run(eval_genomes, 10)
    print('\nWinner fitness:', winner.fitness)


def eval_genomes(genomes, config):
    nn_master = NeuralNetMaster()
    for genome_id, genome in genomes:
        nn_master.eval_genome(genome, config)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'training.cfg')
    run(config_path)
