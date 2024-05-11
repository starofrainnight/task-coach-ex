leadins = """On the other hand,
    This suggests that
    This means that
    It appears that
    Furthermore,
    It follows that
    Analogously,
    Also, 
    Therefore, 
    Clearly,
    Note that
    Of course,
    Suppose, for instance, that
    Thus
    Conversely,
    Rather,
    However, 
    So far,
    Nevertheless,
    For one thing,
    Summarizing, 
    Presumably,
    It may be, then, that
    It must be emphasized that
    Note that """

subjects = """ the house
    the project
    most of the work to be done
    a subset of necessities
    the task at hand
    an important property of these types of projects
    any associated supporting element
    the descriptive power of the base component
    this analysis of the features
    relational information
    the feature developed earlier"""

verbs = """can be described in such a way as to impose
    delimits
    suffices to account for
    cannot be arbitrary in
    is not subject to
    does not readily tolerate
    raises serious doubts about
    is not quite equivalent to
    does not affect the structure of
    may remedy and, at the same time, eliminate
    is not to be considered in determining
    is to be regarded as
    is unspecified with respect to
    is, apparently, determined by
    is necessary to impose an interpretation on
    appears to correlate rather closely with
    is rather different from"""

commands = """Schedule
    Interpret
    Plan
    Rework
    Remedy
    Investigate
    Research
    Construct
    Analyse
    Determine
    Decide"""

objects = """ problems of scope and lead time.
    the details of the work done so far.
    the traditional practice of planning.
    the levels of acceptability from fairly high to virtual gibberish.
    a stipulation to place the constructions into various categories.
    a descriptive fact.
    a gap construction.
    the extended directive discussed in connection with the plan.
    the ultimate standard that determines the accuracy of any proposed plan.
    the system of base rules.
    irrelevant intervening contexts in selected rules.
    an abstract underlying order.
    an important distinction in resource use.
    the strong generative capacity of the schedule."""

import textwrap, random
from itertools import chain, islice


def composeText(partsToUse, line_length=72, times=1):
    parts = []
    for part in partsToUse:
        phraselist = list(map(str.strip, part.splitlines()))
        random.shuffle(phraselist)
        parts.append(phraselist)
    output = chain(*islice(zip(*parts), 0, times))
    return textwrap.fill(" ".join(output), line_length)


def text(times=1, line_length=72):
    return composeText((leadins, subjects, verbs, objects), line_length, times)


def title(line_length=72):
    return composeText((commands, objects), line_length)
