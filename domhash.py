#!/usr/bin/python3

import re
import sys
import base64
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
    __version = "0.0.0.1"
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

    def update_dom(self, new_dom):
        """ allows the user to dynamically update the dom content """
        self.dom = new_dom

    def get_chunk_size(self, base_size=64, scaling_factor=100):
        """ dynamically gets the chunk size to use for hashing """
        length = len(self.dom)
        return base_size + (length // scaling_factor)

    def rolling_hash(self):
        """ basic rolling hash implementation """
        hash_value = 0
        for i, char in enumerate(self.dom):
            hash_value = (hash_value * 31 + ord(str(char))) % (2**32)
        return hash_value

    @staticmethod
    def hash_chunks(chunk):
        """ hash the chunks """
        try:
            sha256 = hashlib.sha256(chunk.encode("utf-8")).digest()
        except AttributeError:
            sha256 = hashlib.sha256(chunk).digest()
        return base64.urlsafe_b64encode(sha256).decode("utf-8")[:6]

    @staticmethod
    def compare_hashes(hash1, hash2):
        """ compare the two hashes together using a simple comparison algorithm """
        min_length = min(len(hash1), len(hash2))
        hash1 = hash1[:min_length]
        hash2 = hash2[:min_length]
        matches = sum(1 for a, b in zip(hash1, hash2) if a == b)
        try:
            # return the match score
            return round((matches / min_length) * 100, 2)
        except ZeroDivisionError:
            raise NoMatchesFound("Total matches returned 0, will not continue")

    def generate_fuzzy_hash(self):
        """ generate the fuzzy hashes from the dom content """
        if self.dom is None:
            raise NoDomContent("There has been no dom content initialized")
        self.__verify_dom_content()
        max_chunks = 10
        block_size = self.get_chunk_size()
        chunks = [self.dom[i:i + block_size] for i in range(0, len(self.dom), block_size)]
        hashed_chunks = [self.hash_chunks(chunk) for chunk in chunks[:max_chunks]]
        combined_hash = ''.join(hashed_chunks)
        return base64.urlsafe_b64encode(hashlib.sha256(combined_hash.encode()).digest()).decode("utf-8")[:64]


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
