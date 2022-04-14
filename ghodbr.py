import os

from github import Github
from dotenv import load_dotenv

load_dotenv()
gh = Github(os.getenv("GITHUB_ACCESS_KEY"))


def get_orgs():
    orgs = []
    for org in gh.get_user().get_orgs():
        orgs.append(org.login)
    return orgs


def get_repos_default_branch(org):
    repos = []
    for repo in gh.get_organization(org).get_repos():
        repos.append([org, repo.name, repo.default_branch])
    return repos


def filtered_repos(run_orgs, old_branch):
    repos = []
    for org in run_orgs:
        org_repos = get_repos_default_branch(org)
        # print(org)
        for repo in org_repos:
            if repo[2] == old_branch:
                repos.append(repo)
                # print(repo)
    return repos


def rename_branch(org, repo, old_name, new_name, dry_run=True):
    log = []
    gh_repo = gh.get_organization(org).get_repo(repo)
    log.append(gh_repo.full_name)
    print(gh_repo)
    # Git reference of the branch that you wish to delete
    source = gh_repo.get_git_ref("heads/" + old_name)

    # Get current default branch protection
    try:
        protection = gh_repo.get_branch(old_name).get_protection()
        print(protection)
    except:
        # Create new branch from old branch
        log.append("create branch " + new_name + " from " + old_name)
        if not dry_run:
            new_default = gh_repo.create_git_ref("refs/heads/" + new_name,
                                                       sha=source.object.sha)

        log.append("set default branch to " + new_name)
        if not dry_run:
            # sleep(1)
            gh_repo.edit(default_branch=new_name)

            # Delete old branch reference
        log.append("delete branch " + old_name)
        if not dry_run:
            source.delete()

    return log


def confirm():
    input_confirm = input("Are you sure? yes/no:")
    if input_confirm == "yes":
        return 0
    return 1


def which_orgs(input_selection, orgs):
    if input_selection == "a":
        # print("Running against all orgs")
        return orgs
    if (int(input_selection) - 1) >= 0:
        # print("Running against " + orgs[int(input_selection) - 1])
        return [orgs[int(input_selection) - 1]]


def main():
    print("Welcome to the GitHub Org Branch Name Changer!")
    input_dryrun = input("Is this a dry run? yes/no: ")
    dry_run = True
    if input_dryrun == "no":
        if confirm() == 0:
            dry_run = False
            print("\n\n*** ARMED! NOT A DRY RUN! ***\n\n")
    input_old_branch = input("Old default branch name: ")
    input_new_branch = input("New default branch name: ")
    orgs = get_orgs()

    for count, org in enumerate(orgs):
        print(count + 1, org)

    print("a all")

    input_org_selection = input("\nOrg number: ")
    run_orgs = which_orgs(input_org_selection, orgs)
    print(run_orgs)
    repos = filtered_repos(run_orgs, input_old_branch)
    for this_repo in repos:
        print(this_repo[1])
    input("Ready. Press enter to continue.")
    if confirm() == 1:
        print("Abort!")
        return 0
    log_out = []
    for repo in repos:
        # rename_branch(org, repo, old_name, new_name, dry_run=True):
        log_out.append(
            rename_branch(repo[0], repo[1], input_old_branch, input_new_branch,
                          dry_run)
        )
    for log in log_out:
        print(log)


main()
