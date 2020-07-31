"""
gen-java-src-db.py

    Generates a Java package/import database, suitable as input for JDVue.
    Also generates Number of Lines of Code statistics, while we're at it.

Usage:
    python gen-java-src-db.py <srcroot> <outfilebase>

  where:
    <srcroot> is the directory at the top of the Java Project source tree.
    <outfilebase> is the base filename to use for the output files.

Output:
    <outfilebase>.db        -- package/import data
    <outfilebase>.nloc.csv  -- line count data

Author: Simon Hunt / July 2020
"""

import os
import sys
import re


def usage_then_exit():
    print(f'Usage: python {sys.argv[0]} <srcroot> <outfilebase>')
    exit(2)


def reslash(s):
    return s.replace('\\', '/')


def clean_dir_name(d):
    d = reslash(d)
    if d.endswith('/'):
        d = d[:-1]
    return d


def get_cmdline_args():
    if len(sys.argv) != 3:
        usage_then_exit()

    srcroot, outfilebase = sys.argv[1:3]
    if not os.path.isdir(srcroot):
        print(f'Not a directory: {srcroot}')
        usage_then_exit()

    srcroot = clean_dir_name(srcroot)
    outfilebase = clean_dir_name(outfilebase)

    return srcroot, outfilebase


def find_java_files(root):
    result = []
    for dir_name, subdir_list, file_list in os.walk(root):
        dname = reslash(dir_name)
        for fname in file_list:
            if fname.endswith('.java'):
                result.append(f'{dname}/{fname}')
    return result


# RE patterns
re_blank = re.compile(r'^\s*$')
re_slash_comment = re.compile(r'^\s*//')
re_single_slashstar = re.compile(r'^\s*/\*.*\*/\s*$')
re_comm_start = re.compile(r'^\s*/\*')
re_comm_end = re.compile(r'^.*\*/')
re_pkg_imp = re.compile(r'^\s*(package|import)')


def remove_slash_star_comments(lines):
    code = []
    incomment = False

    for line in lines:
        start_found = re_comm_start.match(line)
        end_found = re_comm_end.match(line)

        if not incomment and start_found:
            incomment = True
        elif incomment and end_found:
            incomment = False
        elif not incomment:
            code.append(line)

    return code


def analyze_file(javafile):
    with open(javafile) as jf:
        lines = jf.readlines()

    pragmas = [x for x in lines if re_pkg_imp.match(x)]

    loc = [x for x in lines if not re_blank.match(x)]
    ncloc = [x for x in loc
             if not re_slash_comment.match(x) and not re_single_slashstar.match(x)]
    ncloc = remove_slash_star_comments(ncloc)
    stats = len(lines), len(loc), len(ncloc)

    return pragmas, stats


def rmfile(f):
    if os.path.exists(f):
        os.remove(f)


def append_pragmas(javafile, pragmas, dbfile):
    with open(dbfile, 'a') as outf:
        for p in pragmas:
            outf.write(f'{javafile}:{p}')


def append_stats(javafile, stats, csvfile):
    nlin, nloc, nncl = stats
    with open(csvfile, 'a') as outf:
        outf.write(f'{nlin},{nloc},{nncl},{javafile}\n')


def sum_stats(totals, stats):
    for i in range(len(stats)):
        totals[i] += stats[i]


def display_stats(totals):
    nlin, nloc, nncl = totals
    print(f'      nLines...: {nlin}')
    print(f'      nLOC.....: {nloc}')
    print(f'      nNCLOC...: {nncl}')


def process_java_files(outfilebase, file_list):
    dbfile = f'{outfilebase}.db'
    csvfile = f'{outfilebase}.nloc.csv'

    rmfile(dbfile)
    rmfile(csvfile)
    append_stats('Java File', ('nLines', 'nLOC', 'nNCLOC'), csvfile)
    stats_totals = [0, 0, 0]

    for jf in file_list:
        pragmas, nlocstats = analyze_file(jf)
        append_pragmas(jf, pragmas, dbfile)
        append_stats(jf, nlocstats, csvfile)
        sum_stats(stats_totals, nlocstats)

    print(f'  pkg/imp DB file...: {dbfile}')
    print(f'  NLOC stats file...: {csvfile}')
    display_stats(stats_totals)


def main():
    srcroot, outfilebase = get_cmdline_args()
    print('Generating Java Source File Data...\n')

    print(f'  Source root dir...: {os.path.abspath(srcroot)}')

    java_files = find_java_files(srcroot)
    print(f'  Java files found..: {len(java_files)}')

    process_java_files(outfilebase, java_files)
    print()


main()
