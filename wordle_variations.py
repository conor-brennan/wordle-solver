import wordle_graph
import numpy as np
import time
import ujson

## 25 unique letters code

def is_anagram(w1, w2):
    if len(w1)!=len(w2):
        return False
    a1 = [l for l in w1]
    a2 = [l for l in w2]
    for i in range(len(a1)):
        if a1[i] in a2:
            j=a2.index(a1[i])
            a2[j] = "!"
        else:
            return False
    return True

def anagram_free(word_arr):
    d = {}
    afw = []
    for w in word_arr:
        d[w] = w
    for w in word_arr:
        if d[w] is None:
            continue
        d[w] = None
        afw.append(w)
        for wp in word_arr:
            if is_anagram(w,wp):
                d[wp]=None
    return afw

def graph_afw(graph = None):
    guess_words = wordle_graph.guess_words
    possible_words = wordle_graph.possible_words
    if graph is None:
        graph = wordle_graph.load_graph()
    gg={}
    afw = []
    guesses = graph.keys()
    for word in guesses:
        gg[word] = word
    for word in guesses:
        if gg[word] is not None:
            afw.append(word)
            gg[word] = None
            for s in graph[word].keys():
                if "B" not in s:
                    for a in graph[word][s]:
                        gg[a] = None
    return afw

## Wordle Hard Mode code

# this took 7 minutes on my laptop
# the file is 1.5 GB... don't use. I modified the code
def save_graph(graph_path="words/wordle_graph_hard.txt"):
    t1=time.time()
    g={}
    guess_words = wordle_graph.guess_words
    possible_words = wordle_graph.possible_words

    with open(graph_path, "w") as file:
        i = 0
        for wg in guess_words:
            g[wg] = {}
            g[wg]["g"] = {}
            g[wg]["p"] = {}
            # construct guessable words
            for wgp in guess_words:
                score = wordle_graph.get_score(wg,wgp)
                if score in g[wg]["g"]:
                    g[wg]["g"][score].append(wgp)
                else:
                    g[wg]["g"][score] = [wgp]
            # construct possible words
            for wp in possible_words:
                score = wordle_graph.get_score(wg,wp)
                if score in g[wg]["p"]:
                    g[wg]["p"][score].append(wp)
                else:
                    g[wg]["p"][score] = [wp]
            i += 1
            if i%100 == 0:
                t2 = time.time()
                print(f"i: {i}, time: {t2-t1}")

        t2=time.time()
        print(f"{t2-t1} seconds, or {(t2-t1-(t2-t1)%60)/60} mins {(t2-t1)%60} secs")
        ujson.dump(g,file)

def load_hard(graph_path="words/wordle_graph_hard.txt"):
    return wordle_graph.load_graph(hard=True)

hard_graph = None
if __name__ == "__main__":
    try:
        hard_graph = wordle_graph.load_graph()
    except FileNotFoundError:
        print("Could not load word graph. Please ensure graph has been computed and saved.")

# begin strats

# subtracting info so sorting matches with cluster strats
def info_gain(word, n, graph=hard_graph):
    scores = list(graph[word].keys())
    info = 0
    for score in scores:
        info -= (len(graph[word][score])/n)*np.log2(n/len(graph[word][score]))
    return info

def avg_cluster(word, n, graph=hard_graph):
    scores = list(graph[word].keys())
    return n/len(scores)

def weighted_cluster(word, n, graph=hard_graph):
    scores = list(graph[word].keys())
    wc = 0
    for score in scores:
        wc += (len(graph[word][score])**2)/n
    return wc/len(scores)

strats = {
        "info_gain": info_gain,
        "avg_cluster": avg_cluster,
        "weighted_cluster": weighted_cluster
}

def hard_strategies(strategy):
    global strats
    return strats[strategy]

def hard_greedy_words(strategy, graph=hard_graph, num_words=25, all_top=False):
    guesses = list(graph.keys())
    if len(guesses) < num_words:
        num_words = len(guesses)
    pws = {}
    for score in list(graph[guesses[0]].keys()):
        for w in graph[guesses[0]][score]:
            pws[w] = w
    n = len(list(pws.keys()))

    metrics = []
    for wg in guesses:
        metric = hard_strategies(strategy)(wg,n,graph)
        metrics.append([wg,metric])
        if wg in pws.keys():
            pws[wg] = metric
    metrics_sorted = sorted(metrics, key= lambda x:x[1])

    if all_top:
        return metrics_sorted[:num_words]
    
    pw_metrics = []
    for w in pws.keys():
        if pws[w]==metrics_sorted[0][1]:
            pw_metrics.append([w,pws[w]])
    if len(pw_metrics) > 0:
        return pw_metrics
    return metrics_sorted[:num_words]

def is_valid_hard_guess(guess,word,guess_score):
    score = wordle_graph.get_score(guess,word)
    for i in range(len(guess_score)):
        if guess_score[i] == "G" and score[i] != "G":
            return False
        if guess_score[i] == "Y" and score[i] == "B":
            return False
    return True 

def hard_update_word_graph(guess,score,graph):
    new_graph = {}
    for wg in list(graph.keys()):
        if not is_valid_hard_guess(guess,wg,score):
            continue
        new_graph[wg]={}
        for s in list(graph[wg].keys()):
            wx={}
            gy={}
            for word in graph[guess][score]:
                wx[word]=word
            for word in graph[wg][s]:
                if word in wx.keys():
                    gy[word]=word
            if len(list(gy.keys()))>0:
                new_graph[wg][s]=gy
    return new_graph

def hard_avg_score(strategy, starting_word=""):
    scores={1:[],2:[],3:[],4:[],5:[],6:[],"Lose":[]}
    i = 0
    t1 = time.time()
    if starting_word == "":
        starting_word = hard_greedy_words(strategy)[0][0]
    print(starting_word)
    for solution in wordle_graph.possible_words:
        print(solution)
        i += 1
        graph = hard_graph
        done = False
        guesses = 1
        best_word = starting_word
        while not done:
            if best_word == solution:
                done = True
                if guesses > 6:
                    scores["Lose"].append(solution)
                else:
                    scores[guesses].append(solution)
            else:
                graph = hard_update_word_graph(best_word,wordle_graph.get_score(best_word,solution),graph)
            best_word = hard_greedy_words(strategy, graph=graph)[0][0]
            guesses+=1
            
        if i%10==0:
            t2=time.time()
            print(f"{i}: {round(t2-t1,2)} seconds")
        if i%5==0:
            print(f"Current avg: {wordle_graph.avg_from_scores(scores)}")
            print(f"Current fails: {len(scores['Lose'])}")
    return scores

"""
## INFO GAIN LEADERBOARD ##
1. plate - 3.60623, 4 fails (['joker', 'hatch', 'daunt', 'mound'])
2. soare - 3.64471, 7 fails (['daunt', 'jaunt', 'score', 'mound', 'hatch', 'golly', 'patch'])
3. cable - 3.65108, 5 fails (['rover', 'joker', 'daunt', 'foyer', 'shade'])
"""

"""
## AVG CLUSTER LEADERBOARD ##
1. soare - 3.58803, 9 fails (['gaunt', 'patty', 'vaunt', 'maker', 'spore', 'wafer', 'cower', 'watch', 'match'])
"""

## Good info gain words
## ('soare', 'roate', 'raise', 'raile', 'reast', 'slate', 'crate', 'salet', 'irate', 'trace', 'arise', 'orate', 'stare', 'carte', 'raine', 'caret', 'ariel', 'taler', 'carle', 'slane', 'snare', 'artel', 'arose', 'strae', 'carse', 'saine', 'earst', 'taser', 'least', 'alert', 'crane', 'tares', 'seral', 'stale', 'saner', 'ratel', 'torse', 'tears', 'resat', 'alter', 'later', 'prate', 'trine', 'react', 'saice', 'toile', 'earnt', 'trone', 'leant', 'liane', 'trade', 'antre', 'reist', 'coate', 'sorel', 'urate', 'slier', 'teras', 'stane', 'learn', 'trape', 'peart', 'rates', 'paire', 'cater', 'stear', 'roast', 'setal', 'stire', 'teals', 'aline', 'aisle', 'trice', 'reals', 'arles', 'toise', 'scare', 'parse', 'lares', 'oater', 'realo', 'slart', 'laser', 'arets', 'roset', 'aesir', 'saute', 'tries', 'parle', 'rance', 'litre', 'tales', 'heart', 'alone', 'prase', 'store', 'alien', 'share', 'ronte', 'rales', 'grate', 'tared', 'lears', 'stoae', 'soler', 'anile', 'alure', 'terai', 'sared', 'laten', 'urase', 'trail', 'serai', 'siler', 'scrae', 'liart', 'reais', 'siren', 'tiler', 'thrae', 'snore', 'reans', 'ariot', 'derat', 'taels', 'caste', 'crise', 'anise', 'toner', 'scale', 'anole', 'leats', 'tores', 'salue', 'cares', 'maire', 'targe', 'atone', 'caner', 'laers', 'thale', 'renal', 'dealt', 'tires', 'sarge', 'stile', 'corse', 'marse', 'relit', 'spare', 'train', 'plate')
