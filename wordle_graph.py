from words_setup import load_words
import numpy as np
import time
import ujson

guess_words = load_words("wordle_guess.txt",case="lower")
possible_words = load_words("wordle_dict.txt",case="lower")
guess_words = [word for word in guess_words if len(word)==5]
possible_words = [word for word in possible_words if len(word)==5]
guess_words += possible_words       # for some reason, the two dont overlap.

def arr_to_word(word_arr):
    word=""
    for letter in word_arr:
        word=word+letter
    return word

def get_score(guess,answer):
    guess=[l for l in guess]
    answer=[l for l in answer]
    score=["B","B","B","B","B"]
    for i in range(5):
        if guess[i]==answer[i]:
            guess[i]="$"
            answer[i]="!"
            score[i]="G"
    for i in range(len(guess)):
        if guess[i] in answer:
            j=answer.index(guess[i])
            answer[j]="!"
            score[i]="Y"
    return arr_to_word(score)

## USE THIS FUNCTION TO CREATE THE GRAPH BEFORE SOLVING WORDLES
def save_graph(graph_path="words/wordle_graph.txt"):
    t1=time.time()
    g={}
    with open(graph_path, "w") as file:
        i=0
        for wg in guess_words:
            g[wg] = {}
            for wp in possible_words:
                score=get_score(wg,wp)
                if score in g[wg]:
                    g[wg][score].append(wp)
                else:
                    g[wg][score]=[wp]            
            i+=1
            if i%100==0:
                t2=time.time()
                print(f"i: {i}, time: {t2-t1}")
        t2=time.time()
        print(f"{t2-t1} seconds, or {(t2-t1-(t2-t1)%60)/60} mins {(t2-t1)%60} secs")
        ujson.dump(g,file)

def load_graph(graph_path="words/wordle_graph.txt"):
    with open(graph_path, 'r') as file:
        return ujson.load(file)

full_graph = None
if __name__ == "__main__":
    try:
        full_graph=load_graph()
    except FileNotFoundError:
        print("Could not load word graph. Please ensure graph has been computed and saved.")
    
def greedy_info_gain(graph=full_graph,num_words=25):
    t1=time.time()
    guesses=list(graph.keys())
    if len(guesses)<num_words:
        num_words=len(guesses)
    pws={}
    for score in list(graph[guesses[0]].keys()):
        for w in graph[guesses[0]][score]:
            pws[w]=w
    n=len(list(pws.keys()))
##    print(n)
    infos = []
    for wg in guesses:
        scores=list(graph[wg].keys())
        info=0
        for score in scores:
            info+=(len(graph[wg][score])/n)*np.log2(n/len(graph[wg][score]))
        infos.append([wg,info])
        if w in pws.keys():
            pws[w]=info
    infos_sorted = sorted(infos, key=lambda x:x[1])[::-1]
    for w in pws.keys():
        if pws[w]==infos_sorted[0][1]:
            return [[w,pws[w]]]
    t2=time.time()
##    print(f"Took {round(t2-t1,4)} seconds mothafuckaaaaas")
    return infos_sorted[:num_words]

def update_word_graph(guess,score,graph):
    t1=time.time()
    new_graph={}
    for wg in list(graph.keys()):
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
    t2=time.time()
##    print(f"Took {round(t2-t1,4)} seconds")
    return new_graph
            
def get_words(graph):
    guesses=list(graph.keys())
    words=[]
    for score in list(graph[guesses[0]].keys()):
        words+=graph[guesses[0]][score]
    return words

def avg_from_scores(scores):
    n=0
    d=0
    for i in range(1,7):
        n+= i*len(scores[i])
        d+=len(scores[i])
    return n/d
    

def avg_score(starting_word='soare'):
    scores={1:[],2:[],3:[],4:[],5:[],6:[],"Lose":[]}
    i=0
    t1=time.time()
    for solution in possible_words:
        print(solution)
        i+=1
        graph=full_graph
        done=False
        guesses=1
        best_word=starting_word
        while not done:
            if best_word==solution:
                done=True
                if guesses>6:
                    scores["Lose"].append(solution)
                else:
                    scores[guesses].append(solution)
            else:
                graph=update_word_graph(best_word,get_score(best_word,solution),graph)
            best_word=greedy_info_gain(graph=graph)[0][0]
            guesses+=1
            
        if i%10==0:
            t2=time.time()
            print(f"{i}: {round(t2-t1,2)} seconds")
        if i%5==0:
            print(f"Current avg: {avg_from_scores(scores)}")
            print(f"Current fails: {len(scores['Lose'])}")
    return scores

"""
## LEADERBOARD ##
1. salet - 3.54255
2. soare - 3.58056
"""
