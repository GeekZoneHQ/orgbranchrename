# GitHub Org Default Branch Renamer

The [Inclusive Naming Initiative](https://inclusivenaming.org/word-lists/tier-1/#master) states that,
> While master in and of itself is potentially neutral, the propensity in which it is associated with the term slave in computing makes master on its own guilty by association. Though it is used as a standalone, it’s impossible to remove the association with command and control entirely, and thus we recommend moving away from even singular use.
> 
> As the IETF puts it, “Master-slave is an oppressive metaphor that will and should never become fully detached from history.” The word’s origins and historicial use reveal use that is at best chauvinistic and racist, and in almost all cases connotative of ownership. While there is some small ambiguity about the term master, the term slave is unambiguously about the ownership and subjugation of another person, and has been since its inception.
> 
> The terms master/slave are harmful to Black and people of color contributors and employees. Slavery is a tradition barely 3 generations abolished – there are grandparents alive today who were actual, non-metaphorical slaves. Segregation and Apartheid are even more recent. In accordance with most open source codes of conduct and company handbooks, the mandate of all people in a project is to create a welcoming space, regardless of the level of experience, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality. Master/slave are not welcoming words.

In light of this, the GHODBR,
1. searches for all the orgs you have access to, allowing you to select the 
   target
2. searches through all the repos in your org that have the provided old name
3. renames the old name to the new provided default branch name


## Dry Runs
The default mode is dry run. This will only print out the results of the 
search, without actually renaming anything. This allows you to make 
appropriate preparations with all stakeholders before making such a
breaking change.

## Caveats

As you will likely only run this a few times, we have not focused on making 
a shiny GUI for this, it uses a basic CLI.

You will need a [GitHub personal access token](https://github.com/settings/tokens) with admin rights for the org 
you wish to run this on.