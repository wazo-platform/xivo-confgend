#!/usr/bin/env bash
## helper script for manual testing of confgend output
## given two directories as arguments, will compare corresponding files
## using text diff and a more semantic diff

set -euo pipefail


function mkworkdir(){
    mkdir -p $PWD/.diff-tests
    mktemp -p .diff-tests -d
}

function list_pairs(){
    olddir=$(realpath -e --relative-base $PWD $1)
    newdir=$(realpath -e --relative-base $PWD $2)
    find $olddir -type f -exec basename {} \; | while read file; do
        echo $(realpath -e $olddir/$file) $(realpath -e $newdir/$file)
    done
}

diff="git diff --no-index"
flatten_asterisk_conf="python3 $(dirname $0)/flatten_asterisk_conf.py"

function generate_diff(){
    workdir=${WORKDIR:-$(mkworkdir)}
    #reportfile=$workdir/report.txt
    #touch $reportfile
    while read oldfile newfile; do
        echo "$oldfile" "$newfile" 1>&2

        difffile=$workdir/$(basename $oldfile).diff
        $diff $oldfile $newfile > $difffile || true
        # mention diff if not empty
        if test -s $difffile; then
            echo diff $oldfile $newfile $difffile
        fi

        # a utility script is used to flatten config files,
        # by prepending sections to option names,
        # so that line sorting doesn't destroy semantics of configs,
        oldflattened=$workdir/$(echo $oldfile | tr '/' '-').flat
        $flatten_asterisk_conf $oldfile > $oldflattened
        newflattened=$workdir/$(echo $newfile | tr '/' '-').flat
        $flatten_asterisk_conf $oldfile > $newflattened

        # compute sorted diff to check if the same options are present regardless of ordering
        oldsorted=$workdir/$(echo $oldfile | tr '/' '-').flat.sorted
        sort $oldflattened > $oldsorted;
        newsorted=$workdir/$(echo $newfile | tr '/' '-').flat.sorted
        sort $newflattened > $newsorted;

        sorted_difffile=$workdir/$(basename $oldfile).flat.sorted.diff
        $diff $oldsorted $newsorted > $sorted_difffile || true

        if test -s $sorted_difffile; then
            echo sorteddiff $oldfile $newfile $sorted_difffile
        fi
    done
}

list_pairs $@ | generate_diff
