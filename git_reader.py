
import subprocess
import sys
import re
from datetime import datetime as dt

def get_file_diff(repodir, f_path):
    content = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '-p', '--', '{0}'.format(f_path)],
            universal_newlines=True
            )
    return content

"""
Get commit hash list (following time flow)
"""
def get_hashlist_with_author_date(repodir):
    hash_list = []
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--pretty=format:%H,%ai'],
            universal_newlines=True
            ).splitlines()
    hash_list.reverse()  # sort by time

    return_dict = {}
    for row in hash_list:
        h_str, t_str = row.split(',')
        return_dict[h_str] = dt.strptime(t_str, '%Y-%m-%d %H:%M:%S %z')

    return return_dict

def get_numstat(repodir, commit_hash):
    temp_data = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'show', commit_hash, '--numstat', '--pretty='],
            universal_newlines=True
            ).splitlines()
    sum_loc_add = 0
    sum_loc_del = 0
    for row in temp_data:
        loc_add, loc_del, _ = row.split('\t')
        if loc_add==loc_del=="-":
            continue
        sum_loc_add += int(loc_add)
        sum_loc_del += int(loc_del)
    
    
    return sum_loc_add, sum_loc_del


def get_all_tags_with_pattern(repodir, pattern='*.*.*'):
    tag_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'tag', '--list', pattern],
            universal_newlines=True
            ).splitlines()
    return tag_list

def get_all_tags(repodir):
    data_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'show-ref', '--dereference',
             '--hash', '--tags'],
            universal_newlines=True
            ).splitlines()
    hash_list = []
    tag_list = []
    hash_tag_dict = {}
    for row in data_list:
        if len(row.split())==1:
            continue
        temp_hash, temp_tag = row.split()
        hash_list.append(temp_hash)
        tag_list.append(temp_tag)
        hash_tag_dict[temp_hash] = temp_tag
    return hash_list, tag_list, hash_tag_dict


def get_all_hash(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list

def get_all_hash_without_merge(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--no-merges', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list

"""
Get commit hash in a specific interval
"""
def get_hashlist_in_interval(repodir, maxtime, mintime):
    hash_list = []
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--pretty=format:%H,%ai'],
            universal_newlines=True
            ).splitlines()
    hash_list.reverse()  # sort by time

    return_list = []
    for row in hash_list:
        h_str, t_str = row.split(',')
        time_date = dt.strptime(t_str, '%Y-%m-%d %H:%M:%S %z')
        if maxtime >= time_date and mintime <= time_date:
            return_list.append(h_str)

    return return_list


def get_commit_message(repodir, commit_hash):
    commit_msg_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--format=%B',
            '-n', '1', commit_hash],
            universal_newlines=True,
            errors="replace"
            ).splitlines()

    return "\n".join(commit_msg_list)


"""
Get all logs
"""
def git_log_all(dirname):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'log', '--all', '--pretty=fuller'],
            #['git', '-C', '{}'.format(dirname), 'log', '-10', '--pretty=fuller'],
            universal_newlines=True
            )
    return log

def git_log_all_without_merge(dirname):
    log = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'log', '--all', '--pretty=fuller', '--no-merges'],
            #['git', '-C', '{}'.format(dirname), 'log', '-10', '--pretty=fuller'],
            universal_newlines=True
            )
    return log

def get_all_modified_files(repodir, commit_hash):
    files = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'diff-tree', '--no-commit-id',
            '--name-only', '-r', commit_hash,  '--diff-filter=ACMRTUX'],
            universal_newlines=True
            ).splitlines()
    
    return files

def get_entier_file(repodir, commit_hash, f_path):
    try:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}^:{1}'.format(commit_hash, f_path)],
                universal_newlines=True
                )
    except UnicodeDecodeError:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}^:{1}'.format(commit_hash, f_path)]
                ).decode('utf-8','replace')
    
    return content


def get_cur_entier_file(repodir, commit_hash, f_path):
    try:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}:{1}'.format(commit_hash, f_path)],
                universal_newlines=True
                )
    except UnicodeDecodeError:
        content = subprocess.check_output(
                ['git', '-C', '{}'.format(repodir), 'show', '{0}:{1}'.format(commit_hash, f_path)]
                ).decode('utf-8','replace')
    
    return content

def ignore_somecode(text):
    """
    Ignore new pages and CR.
    In git, these are represented as '\r' and '\f'
    If we add '\0' to database, we get error.
    """
    text = re.sub('\r', '', text)
    text = re.sub('\f', '', text)
    text = re.sub('\0', '', text)
    return text

"""
Execute git show
"""
def git_show(dirname, commit_hash):
    show = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show',
             commit_hash],
            ).decode('utf-8', errors='ignore')
    show = ignore_somecode(show)
    return show

"""
Execute git show --unified=0
"""
def git_show_with_context(dirname, commit_hash, context):
    show = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show',
             '--unified={0}'.format(context), commit_hash],
            ).decode('utf-8', errors='ignore')
    show = ignore_somecode(show)
    return show



def git_blame_entire_file(dirname, commit_hash, file_path):
    try:
        text = subprocess.check_output(
                ['git', '-C', '{}'.format(dirname), 'blame', '-l', '-n', '{0}'.format(commit_hash), '--', '{0}'.format(file_path)],
                ).decode('utf-8', errors='ignore')
    except Exception:
        exit('Decode error.')
    text = ignore_somecode(text)
    return text

def get_author_date(dirname, commit_hash):
    date = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show', '{0}'.format(commit_hash), '-s', '--format=%ai'],
            universal_newlines=True
            )
    return date.splitlines()[0]

def get_commit_date(dirname, commit_hash):
    date = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show', '{0}'.format(commit_hash), '-s', '--format=%ci'],
            universal_newlines=True
            )
    return date.splitlines()[0]

def get_author(dirname, commit_hash):
    try:
        author = subprocess.check_output(
                ['git', '-C', '{}'.format(dirname), 'show', '{0}'.format(commit_hash), '-s', '--format=%an'],
                universal_newlines=True
                )
    except UnicodeDecodeError:
        author = subprocess.check_output(
                ['git', '-C', '{}'.format(dirname), 'show', '{0}'.format(commit_hash), '-s', '--format=%an'],
                )
        try:
            author = author.decode('utf-8') # https://docs.python.org/2/library/codecs.html#codec-base-classes
        except UnicodeDecodeError:
            f = open('tmp/UnicodeDecodeError_commit_hash.txt','a')
            f.write('{0}\n'.format(commit_hash))
            author = author.decode('utf-8','ignore') # https://docs.python.org/3.3/howto/unicode.html
            #author = unicode(author, errors='ignore')
            f.close()

    return author.splitlines()[0]


if __name__=="__main__":
    # repodir = '/Users/masanarikondo/paper/2020-PRvsROC'

    # print('bf7ce271a10d840a364b5a356a07b9ce93cf386e: author date')
    # print(get_hashlist_with_author_date(repodir)['bf7ce271a10d840a364b5a356a07b9ce93cf386e'])

    # print('num stat: bf7ce271a10d840a364b5a356a07b9ce93cf386e')
    # print(get_numstat(repodir, 'bf7ce271a10d840a364b5a356a07b9ce93cf386e'))
    # print('num stat: c498e144681dc817b3056f7d968fe3642c23ef9b')
    # print(get_numstat(repodir, 'c498e144681dc817b3056f7d968fe3642c23ef9b'))


    # print('git show: c498e144681dc817b3056f7d968fe3642c23ef9b')
    # print(git_show(repodir, 'c498e144681dc817b3056f7d968fe3642c23ef9b'))

    repodir = '/Users/masanarikondo/paper/2022-dev-communication'
    # f_path = './docs/intro.md'
    f_path='./sections/introduction.tex'
    c = get_file_diff(repodir, f_path)
    print(c)