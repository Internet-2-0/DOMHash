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

def print_ascii_art():
    art = '''
██████╗  ██████╗ ███╗   ███╗██╗  ██╗ █████╗ ███████╗██╗  ██╗
██╔══██╗██╔═══██╗████╗ ████║██║  ██║██╔══██╗██╔════╝██║  ██║
██║  ██║██║   ██║██╔████╔██║███████║███████║███████╗███████║
██║  ██║██║   ██║██║╚██╔╝██║██╔══██║██╔══██║╚════██║██╔══██║
██████╔╝╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║███████║██║  ██║
╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    '''
    print(art)

print_ascii_art()

    def __init__(self):
        super().__init__()
        self.add_argument('domcontent', nargs='?', default=None, help="Pass the DOM content to build the hash from")
        self.add_argument("-h1", "--hash1", default=None, dest="hashOne", help="First hash to compare")
        self.add_argument("-h2", "--hash2", default=None, dest="hashTwo", help="Second hash to compare")
        self.add_argument("-v", "--version", default=False, dest="showVersion", action="store_true", help="Show version and exit")

    def check_args(self, opts):
        """ Check the arguments to verify they are valid """
        if opts.hashOne and not opts.hashTwo:
            raise argparse.ArgumentError(None, "You must pass both hashes for comparison (-h1 and -h2)")
        if opts.hashTwo and not opts.hashOne:
            raise argparse.ArgumentError(None, "You must pass both hashes for comparison (-h1 and -h2)")
        return False

class DomHash:

    # Metadata about the build
    __version = "0.0.0.1"
    __build_type = "beta"
    __build_code_name = "sylvester"
    __build_language = "Python"

    def __init__(self, dom=None):
        self.dom = dom

    @property
    def show_version(self):
        """ Show the version of the build """
        return f"{self.__build_code_name} v{self.__version}({self.__build_type}) -> {self.__build_language}"

    def __verify_dom_content(self):
        """ Ensure the dom content is valid using regex """
        expression = re.compile(r"<.*?>.*?</.*?>", re.DOTALL)
        if not expression.search(self.dom):
            raise HtmlHeuristicIssues("Passed DOM content did not pass heuristic tests")

    def update_dom(self, new_dom):
        """ Update the DOM content dynamically """
        self.dom = new_dom

    def get_chunk_size(self, base_size=64, scaling_factor=100):
        """ Dynamically compute chunk size based on content length """
        length = len(self.dom)
        return base_size + (length // scaling_factor)

    def rolling_hash(self):
        """ Perform a rolling hash """
        hash_value = 0
        for char in self.dom:
            hash_value = (hash_value * 31 + ord(char)) % (2**32)
        return hash_value

    @staticmethod
    def hash_chunks(chunk):
        """ Hash individual chunks """
        try:
            sha256 = hashlib.sha256(chunk.encode("utf-8")).digest()
        except AttributeError:
            sha256 = hashlib.sha256(chunk).digest()
        return base64.urlsafe_b64encode(sha256).decode("utf-8")[:6]

    @staticmethod
    def compare_hashes(hash1, hash2):
        """ Compare two hashes """
        min_length = min(len(hash1), len(hash2))
        matches = sum(1 for a, b in zip(hash1[:min_length], hash2[:min_length]) if a == b)
        if min_length == 0:
            raise NoMatchesFound("No valid hash comparison could be made")
        return round((matches / min_length) * 100, 2)

    def generate_fuzzy_hash(self):
        """ Generate a fuzzy hash from the DOM content """
        if not self.dom:
            raise NoDomContent("No DOM content provided")
        self.__verify_dom_content()
        block_size = self.get_chunk_size()
        chunks = [self.dom[i:i + block_size] for i in range(0, len(self.dom), block_size)]
        hashed_chunks = [self.hash_chunks(chunk) for chunk in chunks[:10]]  # Max 10 chunks
        combined_hash = ''.join(hashed_chunks)
        return base64.urlsafe_b64encode(hashlib.sha256(combined_hash.encode()).digest()).decode("utf-8")[:64]

if __name__ == "__main__":
    try:
        parser = Parser()
        opts = parser.parse_args()

        dom = DomHash()

        if opts.showVersion:
            print(dom.show_version)
        else:
            if opts.domcontent:
                dom.update_dom(opts.domcontent)
                print(dom.generate_fuzzy_hash())
            elif opts.hashOne and opts.hashTwo:
                print(dom.compare_hashes(opts.hashOne, opts.hashTwo))
            else:
                parser.print_help()

    except argparse.ArgumentError as e:
        print(f"Argument Error: {e}")
    except NoDomContent as e:
        print(f"Error: {e}")
    except HtmlHeuristicIssues as e:
        print(f"Error: {e}")
    except NoMatchesFound as e:
        print(f"Error: {e}")
