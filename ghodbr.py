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


def get_repos_default_branch(org: str):
    repos = []
    for repo in gh.get_organization(org).get_repos():
        repos.append([org, repo.name, repo.default_branch])
    return repos


def filtered_repos(org, old_branch):
    repos = []
    org_repos = get_repos_default_branch(org)
    for repo in org_repos:
        # print(repo)
        if repo[2] == old_branch:
            repos.append(repo)
    return repos


def rename_branch(org: str, repo: str, old_branch: str, new_branch: str,
                  dry_run: bool = True):
    log = []
    gh_repo = gh.get_organization(org).get_repo(repo)
    log.append(gh_repo.full_name)
    print(gh_repo)
    # Git reference of the branch that you wish to delete
    source = gh_repo.get_git_ref("heads/" + old_branch)

    # Get current default branch protection
    try:
        protection = gh_repo.get_branch(old_branch).get_protection()
        print(protection)
    except:
        # Create new branch from old branch if branch protection does not exist
        log.append("create branch " + new_branch + " from " + old_branch)
        if not dry_run:
            new_default = gh_repo.create_git_ref("refs/heads/" + new_branch,
                                                 sha=source.object.sha)

        log.append("set default branch to " + new_branch)
        if not dry_run:
            # sleep(1)
            gh_repo.edit(default_branch=new_branch)

            # Delete old branch reference
        log.append("delete branch " + old_branch)
        if not dry_run:
            source.delete()

    return log


def confirm():
    input_confirm = input("Are you sure? yes/no:")
    if input_confirm == "yes":
        return 0
    return 1


# get open issues
def get_issues(org: str, repo: str):
    gh_repo = gh.get_organization(org).get_repo(repo)
    issues = []
    for issue in gh_repo.get_issues(state="open"):
        issues.append(issue)
    return issues


# check if rename branch issue exists
def check_rename_branch_issue(issues: list, old_branch: str, new_branch: str):
    for issue in issues:
        if issue.title == "Rename Branch " + old_branch + " to " + new_branch:
            print("Issue already exists")
            return issue
    return 0


# close issue, for use when rename branch is successful
def close_issue(issue: object):
    issue.edit(state="closed")
    print("Issue closed")
    return 0


def create_issue(org: str, repo: str, old_branch: str, new_branch: str,
                 dry_run: bool = True):
    gh_repo = gh.get_organization(org).get_repo(repo)
    body = "This repo has the the default branch set to `" + old_branch + "`."
    body += "\n\n"
    body += "Please rename the branch to `" + new_branch + "`."
    body += "\n\n"
    body += "Reference:\n"
    body += "- [Inclusive Naming Initiative](https://inclusivenaming.org/word-lists/tier-1/)\n"
    body += "- [GitHub's Inclusive Naming Policy](https://help.github.com/articles/about-repository-naming-guidelines-for-github-enterprise-and-gitlab-enterprise-repositories/)\n"
    body += "- [Internet Engineering Task Force](https://tools.ietf.org/id/draft-knodel-terminology-02.html)\n"
    body += "- [NCSC](https://www.ncsc.gov.uk/blog-post/terminology-its-not-black-and-white)\n"
    title = "Rename Branch " + old_branch + " to " + new_branch

    if not dry_run:
        return gh_repo.create_issue(title=title, body=body).number
    return 0


def issue_loop(repos, old_branch, new_branch, dry_run):
    issues_out = []
    for repo in repos:
        issues = get_issues(repo[0], repo[1])
        issue = check_rename_branch_issue(issues,
                                          old_branch,
                                          new_branch)
        if issue == 0:
            issue = create_issue(org=str(repo[0]),
                                 repo=str(repo[1]),
                                 old_branch=old_branch,
                                 new_branch=new_branch,
                                 dry_run=dry_run)
        issues_out.append([repo[0], repo[1], issue.number, issue.html_url])

        print("Repo:         " + str(repo))
        print("Issue number: " + str(issue.number) + "\n")
    with open("issues.txt", "w") as f:
        f.writelines(str(issues_out))
    return 0


def branch_loop(repos, old_branch, new_branch, dry_run):
    for repo in repos:
        log = rename_branch(org=repo[0],
                            repo=repo[1],
                            old_branch=old_branch,
                            new_branch=new_branch,
                            dry_run=dry_run)
        print("\n".join(log))
    with open("repos.txt", "w") as f:
        f.writelines(str(log))
    return 0


def main():
    actions = {"i": "create issue for each repo, 0 if dry run",
               "r": "rename branches", }
    print("Welcome to the GitHub Org Branch Name Changer!")
    for action in actions:
        print(action + ": " + actions[action])

    input_selection = input("Select action: ")
    input_dry_run = input("Dry run? yes/no: ")
    dry_run = True
    if input_dry_run == "no":
        dry_run = False
        print("Dry run: " + str(dry_run))

    input_old_branch = input("Old branch name: ")
    input_new_branch = input("New branch name: ")

    all_orgs = get_orgs()
    for count, org in enumerate(all_orgs):
        print(str(count + 1) + ": " + org)
    input_orgs = int(input("Run against which org: ")) - 1
    run_org = "".join(all_orgs[input_orgs:input_orgs + 1])
    repos = filtered_repos(run_org, input_old_branch)
    print("Run against org: " + run_org)
    print("Found " + str(len(repos)) + " repos with branch " +
          input_old_branch)
    print("Repos: ")
    for repo in repos:
        print(repo)
    print("Old branch: " + input_old_branch)
    print("New branch: " + input_new_branch)
    print("Action: " + str(actions[input_selection]))
    print("Dry run: ***" + str(dry_run) + "***")

    if confirm() != 0:
        print("Exiting")
        return 0

    if input_selection == "i":
        issue_loop(repos, input_old_branch, input_new_branch, dry_run)
        return 0

    branch_loop(repos, input_old_branch, input_new_branch, dry_run)
    return 0


main()
