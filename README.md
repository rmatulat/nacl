# NACL Toolkit

## Introduction
The nacl toolkit provides some scripts to help salt administrators to keep track of changes in their salt environment.
Because a pillar and state codebase may quickly grow to a mess of git repositories we started developing a set of tools to manage our codebase in an easy way.

## Saltstack and Gitlab
We make an excessive use of git in our saltstack codebase and every git repository has its origin on a local gitlab service.
We like codereviews to ensure that changes in our infrastructure are well known by other admins. We also try to develop our code in local sandboxes in a decentralized manner, like in VMs, so that we will harm our production site as less as possible.

A heavy use of git repositories for all states and pillars might be confusing at times when it comes to questions like 'do I have the latest commit of X?', 'do I need to push Y?' or 'what are my mergerequests are doing?'.

So we did some scripting to make life easier, because we expect to grow our infrastructure to dozens of states and pillars in the upcomming years.

## THIS IS BETA SOFTWARE!
nacl is in a very early stage, so if you like to check it out, you are welcome, BUT:
THERE IS NO WARRANTY!

## Installation
TODO

## Usage
TODO

But mainly `nacl-* -h`

