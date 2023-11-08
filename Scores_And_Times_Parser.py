def scores_and_times(level,score=0,time=0,mode="write"):
    level = level
    writing = (mode=="write")
    if not(writing): mode = mode
    f_old = open("Scores_And_Times.txt","r")
    f_rows = list(f_old.read().split("\n"))
    f_score_lists = [[int(fscore) for fscore in f_rows[2*i].split(":")[1].split(",")] for i in
                     range(0,round(len(f_rows)/2)) ]
    f_time_lists = [[int(ftime) for ftime in f_rows[2 * i + 1].split(":")[1].split(",")] for i in
                     range(0, round(len(f_rows) / 2))]
    print(f_score_lists)
    print(f_time_lists)
    f_score_lists[level].append(score)
    f_time_lists[level].append(time)
    f_old.close()
    if writing:
        f = open("Scores_And_Times.txt","w")
        for i, scores in enumerate(f_score_lists):
            sline = "level "
            sline += str(i)
            sline += " scores: "
            sline += str(scores).replace("[", "").replace("]", "")
            sline += "\n"
            f.write(sline)
            tline = "level "
            tline += str(i)
            tline += " times: "
            tline += str( f_time_lists[i] ).replace("[", "").replace("]", "")
            tline += "\n"
            f.write(tline)
        f.close()
    else:
        if mode == "scores":
            return f_score_lists[level]
        elif mode == "times":
            return f_time_lists[level]
        else:
            raise ValueError

def clear_scores_and_times():
    f_old = open("Scores_And_Times.txt","r")
    f_rows = list(f_old.read().split("\n"))
    f_score_lists = [[int(fscore) for fscore in f_rows[2*i].split(":")[1].split(",")] for i in
                     range(0,round(len(f_rows)/2)) ]
    f = open("Scores_And_Times.txt", "w")
    for i, scores in enumerate(f_score_lists):
        sline = "level "
        sline += str(i)
        sline += " scores: 0"
        sline += "\n"
        f.write(sline)
        tline = "level "
        tline += str(i)
        tline += " times: 0"
        tline += "\n"
        f.write(tline)
    f.close()