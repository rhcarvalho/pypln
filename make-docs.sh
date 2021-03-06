#!/bin/bash

if [ ! -z "$(git status | grep '# Untracked files:')" ]; then
    echo "Sorry, I can't make docs because you have untracked files."
    echo 'Please move them from here, delete or even commit them.'
    echo 'Run "git status" to see which files are untracked.'
    exit 1
fi

TMP_DIR=/tmp/pypln-docs
current_branch=$(git branch | grep '*' | cut -d ' ' -f 2)

# Temporary directory to store static files
rm -rf $TMP_DIR
mkdir $TMP_DIR
touch $TMP_DIR/.nojekyll
cp .gitignore $TMP_DIR/

# Stash changes
git stash save "saved to build doc" || exit 1
git checkout develop

# Make Sphinx documentation
cd doc
make html
cd ..
mv doc/_build/html/* $TMP_DIR/
rm -rf doc/_build

# Make Reference documentation using epydoc
echo "Building Api Docs with EpyDoc..."
epydoc -v -u https://github.com/namd/pypln --debug --graph=all --parse-only --html --no-frames -o $TMP_DIR/reference pypln/ || exit 1

git checkout gh-pages
rm -rf *
mv $TMP_DIR/* $TMP_DIR/.gitignore $TMP_DIR/.nojekyll .
rm -rf $TMP_DIR
git add .
git commit -m 'Docs built automatically by make-docs.sh'
git checkout $current_branch
git stash pop
