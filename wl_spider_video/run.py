import subprocess
import multiprocessing
import sys


def scrapy():
    p = subprocess.Popen("scrapy crawl iqiyi")
    p.communicate()


if __name__ == '__main__':
    num = sys.argv[1]
    if not num.isdigit() and not 1 < int(num) < 4:
        print("参数错误")
    process_list = [multiprocessing.Process(target=scrapy) for i in range(int(num))]
    for process in process_list:
        process.start()
    for process in process_list:
        process.join()
