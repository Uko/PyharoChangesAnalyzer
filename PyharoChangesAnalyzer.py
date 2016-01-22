#!/usr/bin/env python3

from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import os
import shutil
import re


INTERESTING_CHANGE_TYPES = ["A", "M", "R"]


def clone_init_repo():
    repo = Repo.clone_from("https://github.com/pharo-project/pharo-core.git","pharo-repo")

def analyze_tag(tag):
    print(tag.name)

    if os.path.exists(tag.name):
        os.remove(tag.name)

    commit = tag.commit
    if len(commit.parents) == 0:
        return

    diff = commit.parents[0].diff(commit)
    log = ""

    for change_type in INTERESTING_CHANGE_TYPES:
        for change in diff.iter_change_type(change_type):
            path_segments = change.a_path.split("/")
            path_segments.reverse()
            if path_segments[0].endswith(".st"):
                if path_segments[2] == "instance":
                    log += inst_method_string_from_segments(path_segments)
                elif path_segments[2] == "class":
                    log += cls_method_string_from_segments(path_segments)
                elif len(path_segments) >= 4 and path_segments[3] == "extension":
                    if path_segments[1] == "instance":
                        log += ext_inst_method_string_from_segments(path_segments)
                    if path_segments[1] == "class":
                        log += ext_cls_method_string_from_segments(path_segments)
                else:
                    log += class_string_from_segments(path_segments)

                log += "\n"

    print(log + "\n")
    with open(tag.name, "w") as version_file:
        version_file.write(log)

def inst_method_string_from_segments(segments):
    return segments[3][:-6] + '>>#' + recoverSelector(segments[0])

def cls_method_string_from_segments(segments):
    return segments[3].replace(".", " ") + '>>#' + recoverSelector(segments[0])

def ext_inst_method_string_from_segments(segments):
    return segments[2] + '>>#' + recoverSelector(segments[0])

def ext_cls_method_string_from_segments(segments):
    return segments[2] + ' class' + '>>#' + recoverSelector(segments[0])

def class_string_from_segments(segments):
    return segments[1][:-6]

def recoverSelector(name):
    return name[:-3].replace("_", ":").replace("%5F","_")



try:
    repo = Repo("pharo-repo")
    repo.remotes.origin.pull()
except InvalidGitRepositoryError:
    shutil.rmtree("pharo-repo")
    clone_init_repo()
except NoSuchPathError:
    clone_init_repo()

tags_of_pharo5 = (tag for tag in repo.tags if re.match("^5\d{4}$", tag.name))

for tag in tags_of_pharo5:
    analyze_tag(tag)