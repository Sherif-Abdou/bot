import discord
import wikipedia
import os
import logging
from re import subn, match
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.plotting.plot import plot3d
from googletrans import Translator
from PyDictionary import PyDictionary
from chem_src import balance_stoichiometry, Substance
from chempy.util import periodic


REGEX="(\d)([a-zA-Z])|(\(.*\))(\(.*\))"
RREGEX="(\d)\*([a-zA-Z])|(\(.*\))\*(\(.*\))"

translator = Translator()

dictionary=PyDictionary()

class Handler:
    handlers = []

def parse_eq(equation):
    eq = equation.replace("^", "**")
    times = 1
    def m(match):
        pair = (1, 2) if match.group(1) is not None else (3, 4)
        return match.group(pair[0])+"*"+match.group(pair[1])
    while times != 0:
        eq, times = subn(REGEX, m, eq)
    return eq

def message_handler(regex, action):
    regex += "(.*)"
    def handler(func):
        async def wrapper(*args, **kwargs):
            string = kwargs["string"]
            m = match(regex, string)
            if m is None:
                return False
            rest = m.groups()[-1].strip()
            kwargs["m"] = m
            channel = kwargs["channel"]
            await channel.send(f"{action}...")
            logging.info(f"{action}: {string}")
            res = ""
            print(rest)
            print(func)
            try:
                res = func(rest, *args, **kwargs)
                pass
            except Exception as err:
                logging.error(err)
                res = f"Error {action}"
            if not isinstance(res, str):
                await res
                return True
            await channel.send(res)
            return True
        Handler.handlers.append((regex, wrapper))
        return wrapper
    return handler

def reverse_parse_eq(equation, *args, **kwargs):
    eq = equation.replace("**", "^")
    times = 1
    def m(match):
        pair = (1, 2) if match.group(1) is not None else (3, 4)
        return match.group(pair[0])+match.group(pair[1])
    while times != 0:
        eq, times = subn(RREGEX, m, eq)
    return eq

def to_string(res):
    res_str = pretty(res, use_unicode=True).replace("*", "\\*")
    return f"```\n" + res_str + "\n```"""

@message_handler("\\?\\?factor", "Factoring")
def factor_equation(equation, *args, **kwargs):
    eq = parse_eq(equation)
    res = factor(parse_expr(f"{eq}"))
    return to_string(res)

@message_handler("\\?\\?simplify", "Simplifying")
def simplify_equation(equation, *args, **kwargs):
    eq = parse_eq(equation)
    res = simplify(parse_expr(eq))
    return to_string(res)

@message_handler("\\?\\?expand", "Expanding")
def expand_equation(equation, *args, **kwargs):
    eq = parse_eq(equation)
    res = expand(parse_expr(f"{eq}"))
    return to_string(res)


@message_handler("\\?\\?solve", "Solving")
def solve_equation(equation, *args, **kwargs):
    eq = parse_eq(equation)
    split = eq.split("=")
    if len(split) == 2:
        eq = Eq(parse_expr(split[0]), parse_expr(split[1]))
    res = solveset(eq, [symbols(str(v)) for v in eq.free_symbols][0])
    logging.info(res)
    stringed = to_string(res)
    stringed = "Restricted Domain to all Real Numbers\n" + stringed
    return stringed

@message_handler("\\?\\?graph", "Graphing")
def graph_equation(equation, channel=None, *args, **kwargs):
    eq = parse_eq(equation)
    parsed = parse_expr(eq).evalf()
    import matplotlib.pyplot as plt
    pl = None
    if len(parsed.free_symbols) == 2:
        pl = plot3d(parsed, show=False, backend="matplotlib")
    else:
        pl = plot(parsed, show=False, backend="matplotlib")
    backend = pl.backend(pl)

    backend.process_series()
    backend.fig.savefig('/tmp/output.png', dpi=300)
    return channel.send('Graph', file=discord.File('/tmp/output.png', '/tmp/output.png'))
    

@message_handler("\\?\\?([a-z]{2}) ", "Translating")
def translate(text, m=None, *args, **kwargs):
    print(text)
    to_lang = m.group(1)
    print(to_lang)
    res = translator.translate(text, dest=to_lang).text
    return res

def merge_array(arr):
    return ", ".join(arr)

@message_handler("\\?\\?def", "Defining")
def define_word(word, *args, **kwargs):
    words = word.split()[0]
    is_austin =  words == "hubris"
    res = dictionary.meaning(words)
    full =  "\n".join([f"{key}: {merge_array(value)}" for key, value in res.items()])
    return full if not is_austin else "Austin, literally Austin\n\n" + full

@message_handler("\\?\\?syn", "Finding Synonyms")
def syn_word(word, *args, **kwargs):
    words = word.split()[0]
    is_austin =  words.lower() == "hubris"

    res = dictionary.synonym(words)
    return merge_array(res) if not is_austin else "Austin, literally Austin\n\n" + merge_array(res)

@message_handler("\\?\\?ant", "Finding Antonyms")
def syn_word(word, *args, **kwargs):
    words = word.split()[0]

    res = dictionary.antonym(words)
    return merge_array(res) 

@message_handler("\\?\\?stoi", "Doing chem magic")
def stoi_formulae(formula, *args, **kwargs):
    def element_uni(element):
        return Substance.from_formula(element).unicode_name

    parts = formula.split(";")
    parts = [set(part.strip().split()) for part in parts]
    if len(parts) != 2:
        return "Need two sides seperated by a ;"
    res =  [dict(s) for s in balance_stoichiometry(*parts)]
    stringed = ["\n".join([f"{element_uni(element)}: {count}" for element, count in r.items()]) for r in res]
    return f"From:\n{stringed[0]}\n\nTo:\n{stringed[1]}"

table = {}
for i, (name, symbol) in enumerate(zip(periodic.names, periodic.symbols)):
    table[str(i)] = i
    table[name] = i
    table[symbol] = i

@message_handler("\\?\\?per", "Searching the table")
def search_table(keyword, *args, **kwargs):
    term = keyword.strip()
    num =  table[term]
    return f"{num}; Name: {periodic.names[num]}; Symbol: {periodic.symbols[num]}; Mass: {periodic.relative_atomic_masses[num]}"

