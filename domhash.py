#!/usr/bin/python3

import re
import sys
import hashlib
import argparse

class NoMatchesFound(Exception): pass


class NoDomContent(Exception): pass


class HtmlHeuristicIssues(Exception): pass


class Parser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()

    @staticmethod
    def check_args(opts):
        """ check the arguments to verify that you aren't screwing up """
        found_error = False
        if opts.hashOne and not opts.hashTwo:
            print("You did not pass a secondary hash to compare against")
            found_error = True
        elif opts.hashTwo and not opts.hashOne:
            print("You did not pass a primary hash to compare against")
            found_error = True
        return found_error

    @staticmethod
    def optparse():
        """ self contained argument parser """
        parser = argparse.ArgumentParser()
        pos_args = parser.add_argument_group("Positional Arguments")
        pos_args.add_argument(
            'domcontent', nargs='?', default=None,
            help="Pass the dom content to build the hash from"
        )

        misc_args = parser.add_argument_group("Misc Arguments")
        misc_args.add_argument(
            "-h1", "--hash1", default=None, dest="hashOne",
            help="Pass a built hash to compare to another hash (requires -h2 to be passed)"
        )
        misc_args.add_argument(
            "-h2", "--hash2", default=None, dest="hashTwo",
            help="Pass another built hash to compare to first hash (requires -h1 to be passed)"
        )
        misc_args.add_argument(
            "-v", "--version", default=False, dest="showVersion", action="store_true",
            help="Print the version number and exit"
        )

        return parser.parse_args()



class DomHash(object):

    # version: major.minor.patch.push
    __version = "0.1.1.2"
    # build type
    __build_type = "beta"
    # build code name
    __build_code_name = "sylvester"
    # build language
    __build_language = "Python"

    def __init__(self, dom=None):
        self.dom = dom

    @property
    def show_version(self):
        """ show the build version """
        return f"{self.__build_code_name} v{self.__version}({self.__build_type}) -> {self.__build_language}"

    def __verify_dom_content(self):
        """ verify that the dom content is a type of markdown with regex (can also use XML) """
        expression = re.compile(r"\<.*?\>(.*?)\<.*?\>")
        if expression.search(self.dom) is None:
            raise HtmlHeuristicIssues("Passed dom content did not pass heuristic tests")

    def __clean_html(self):
        """ cleans the HTML content into workable data """
        self.dom = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', self.dom)
        self.dom = re.sub(r'<[^>]+>', '', self.dom)
        self.dom = re.sub(r'&[a-z]+;', ' ', self.dom)
        self.dom = re.sub(r'\s+', ' ', self.dom).strip()

    def update_dom(self, new_dom, minimum_size=20):
        """ allows the user to dynamically update the dom content """
        self.dom = new_dom
        self.__clean_html()
        if len(self.dom) < minimum_size:
            raise HtmlHeuristicIssues("Not enough data to continue")

    def tokenize(self, ngrams=5):
        """ create tokens from tyhe dom content """
        words = self.dom.split()
        tokens = [' '.join(words[i:i+ngrams]) for i in range(len(words)-ngrams+1)]
        return tokens

    @staticmethod
    def hash_chunks(chunk):
        """ hash the chunks """
        return hashlib.sha256(chunk.encode("utf-8")).hexdigest()

    @staticmethod
    def compare_hashes(hash1, hash2):
        """ changes the way we compare to using the Jaccard similarity algorithm """
        test1, test2 = set(hash1), set(hash2)
        intersection = test1.intersection(test2)
        union = test1.union(test2)
        if not union:
            return 0
        return len(intersection) / len(union)

    def hash(self):
        """ implements a `hash` function """
        return self.generate_fuzzy_hash()

    def digest(self, is_set=True):
        """ gcreate the digest of the tokens """
        tokens = self.tokenize(ngrams=5)
        if is_set:
            return set(self.hash_chunks(chunk) for chunk in tokens)
        else:
            return [self.hash_chunks(chunk) for chunk in tokens]

    def generate_fuzzy_hash(self):
        combined_hash = ''.join(self.digest(is_set=False))
        return combined_hash[:64] if len(combined_hash) >= 64 else combined_hash.ljust(64, '0')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("USAGE: domhash.py [domcontent] [-h1 HASH -h2 HASH]")
    else:
        opts = Parser().optparse()
        if not Parser.check_args(opts):
            dom = DomHash()
            if opts.showVersion:
                print(dom.show_version)
            else:
                if opts.domcontent is not None:
                    dom.update_dom(opts.domcontent)
                    print(dom.generate_fuzzy_hash())
                else:
                    if opts.hashOne is not None:
                        print(dom.compare_hashes(opts.hashOne, opts.hashTwo))
        else:
            print("USAGE: domhash.py [domcontent] [-h1 HASH -h2 HASH]")
