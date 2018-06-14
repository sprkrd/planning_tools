import re

from matplotlib import pyplot as plt

PROBLEM_FILE_RE = re.compile(r"p[0-9]+\.pddl")

def linspace(a, b, n):
    for i in range(n):
        yield a + i*(b-a)/(n-1)
        
        
def plot_results_actl(alphas, plan_prob, plan_len, plan_cost):
    fig, axs = plt.subplots(2, 1, sharex=True)
    fig.subplots_adjust(hspace=0.05)
    # fst plot
    axs[0].plot(alphas, plan_len, color="b")
    axs[0].set_ylabel("Plan length")
    axs[0].grid("on")
    ax0tw = axs[0].twinx()
    ax0tw.plot(alphas, plan_cost, color="r")
    ax0tw.set_ylabel("Plan cost")
    axs[0].yaxis.label.set_color("b")
    ax0tw.yaxis.label.set_color("r")
    for t in axs[0].get_yticklabels():
        t.set_color("b")
    for t in ax0tw.get_yticklabels():
        t.set_color("r")
    # snd plot
    axs[1].plot(alphas, plan_prob, "b")
    axs[1].set_xlabel(r"$ \alpha $")
    axs[1].set_ylabel("Success probability")
    min_y = min(plan_prob)
    max_y = min(1.0, max(plan_prob)*1.1)
    axs[1].set_yticks(list(linspace(min_y, max_y, 6)))
    axs[1].grid("on")
    plt.show()
    
def print_plan(title, plan):
    print(title + " ({} actions):".format(len(plan)))
    print("  " + "\n  ".join("({})".format(" ".join(a)) for a in plan))