# Copyright (C) 2019 Elia Bonetto, Filippo Rigotto, Luca Attanasio, Francesco Savio
# Under MIT license: see LICENSE file in root directory

import os
from strategy import *
from base_options import *
from ipdmp import IPDRoundRobin
from player import MultiPlayer

def main():
    root = os.path.dirname(os.path.abspath(__file__))[:-5]

    opt = BaseOptions().parse(BaseOptions.RIPDMP_C)
    NUM_ITER = opt.niter
    NUM_PLAYERS = opt.nplay
    NUM_REPETITIONS = 0 # arg override
    MAX_ALLOWED = opt.maxrep
    PERCENTAGE = opt.percent
    FIXED = opt.fixed
    SAVE_IMG = opt.saveimg
    LATEX = opt.latex
    np.random.seed(opt.seed) # None = clock, no-number = 100

    print("Testing repeated round-robin tournament with {}-people".format(NUM_PLAYERS))

    # define population
    k_strategies = Strategy.generatePlayers(NUM_PLAYERS, replace=(NUM_PLAYERS>Strategy.TOT_STRAT), fixed=FIXED)

    repeated_players = [] # strategies evolution
    unique, counts = np.unique(k_strategies, return_counts=True)
    strategies_df = pd.DataFrame([counts],columns=unique)

    while np.unique(k_strategies, return_counts=True)[1].max() < k_strategies.size*3/4 and NUM_REPETITIONS < MAX_ALLOWED:
        NUM_REPETITIONS += 1
        print("Reached rep {} of max {}".format(NUM_REPETITIONS, MAX_ALLOWED))

        # initialize players with given strategies
        players = np.array([MultiPlayer(k) for k in k_strategies])

        players = IPDRoundRobin(players, NUM_ITER) # no strategy change, not against itself
        repeated_players.append(players)

        # create strategies history
        unique, counts = np.unique(k_strategies, return_counts=True)
        df = pd.DataFrame([counts],columns=unique)
        strategies_df = strategies_df.append(df)

        for i in range(0,int(NUM_PLAYERS * PERCENTAGE)):
            k_strategies = np.append(k_strategies, players[i].s.id)
            k_strategies = np.delete(k_strategies, np.argmax(players[NUM_PLAYERS-i-1].s.id))

    if np.unique(k_strategies, return_counts=True)[1].max() >= k_strategies.size*3/4:
        print("Convergence speed of round-robin tournament is {} with {}-people".format(NUM_REPETITIONS, NUM_PLAYERS))
    else:
        print("Convergence not reached")

    # save plots
    strategies_df = strategies_df.rename(index=str,
        columns={-3: "GrimTrigger", -2: "TitFor2Tat", -1: "TitForTat", 0: "Nice", 100: "Bad", 50: "Indifferent"})
    for c in strategies_df.columns:
        if str.isdigit(str(c)):
            if c > 50:
                strategies_df = strategies_df.rename(index=str, columns={c: "MainlyBad (k={})".format(c)})
            else:
                strategies_df = strategies_df.rename(index=str, columns={c: "MainlyNice (k={})".format(c)})

    strategies_df.index = np.arange(strategies_df.index.size)
    strategies_df = strategies_df.fillna(0).astype(int)

    if LATEX:
        print(strategies_df.T.to_latex())
    else:
        print(strategies_df.T)

    fig = strategies_df.plot(figsize=(12,5))
    plt.legend(bbox_to_anchor=(0,-0.1), ncol=5, loc=2)
    plt.title('Strategies evolution')
    plt.ylabel('Number of strategies')
    plt.xlabel('Time')
    fig.xaxis.set_major_locator(MaxNLocator(integer=True))
    if SAVE_IMG:
        plt.savefig('{}/img/ripdmp-const/ripdmp-evolution-const-pop-{}.eps'.format(root, NUM_PLAYERS),format='eps',bbox_inches='tight')
        plt.close()
    else:
        plt.show()

    for (r, players) in zip(np.arange(NUM_REPETITIONS), repeated_players):
        plt.figure(figsize=(12,5))
        for p in players:
            points = p.get_points()
            plt.plot(points, label=p.s)
            plt.title("Multi pl. game: {}".format(NUM_PLAYERS))
            plt.xlabel('Match number')
            plt.ylabel('Points')
        plt.legend(bbox_to_anchor=(0,-0.1), ncol=5, loc=2)

        if SAVE_IMG:
            plt.savefig('{}/img/ripdmp-const/ripdmp-scores-const-pop-{}-r{}.eps'.format(root, NUM_PLAYERS, r),format='eps',bbox_inches='tight')
            plt.close()
        else:
            plt.show()

if __name__ == "__main__":
    main()
