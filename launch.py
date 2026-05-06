from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()

    #
    
    #print("Number of unique pages crawled: " + str(len(unique_pages_crawled)))
    #print("Number of unique pages found: " + str(len(unique_pages_found)))
    #print("Longest Page: " + longest_page + " - ")
    #print("Raw Content Size: " + str(longest_page_len))
    #print("Header Size: " + str(longest_page_header))

    #ct = 0
    #for pair in sorted(word_dict.items(), key=lambda item: item[1], reverse = True): # sort with lambda function + built in sorted()
    #   print(f"{pair[0]}\t{pair[1]}")
    #    ct += 1
    #    if (ct > 50):
    #        break

    #print("crawled subdomains:")
    #for pair in sorted(crawled_subdomains.items(), key=lambda item: item[1], reverse = True): # sort with lambda function + built in sorted()
        #print(f"{pair[0]}\t{pair[1]}")

    #print("found subdomains:")
    #for pair in sorted(crawled_subdomains.items(), key=lambda item: item[1], reverse = True): # sort with lambda function + built in sorted()
        #print(f"{pair[0]}\t{pair[1]}")
        


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
