#Git Workflow

###Remote Development

For now, we'll be using a [fork-pull model](https://help.github.com/articles/using-pull-requests/).

We may move to a shared repository model in the future.


###Local Development

Locally, I use a branch and merge (or rebase) workflow.

1. Create a new local branch with `git checkout -b experimental`.
2. Commit as usual. You can confirm you're on the experimental branch with `git branch -a`.
3. If all changes in your branch have been committed, you can switch back to your original branch and merge there with `git checkout master` and `git merge experimental`.

If there are commits in both your original and experimental branches, we can looking into using [git rebase](http://git-scm.com/book/en/Git-Branching-Rebasing).


###Useful Commands

* Shorthand status: `git status -s`
* Commit all with a message: `git commit -am 'Updated the message'`
* See the log: `git log --oneline`