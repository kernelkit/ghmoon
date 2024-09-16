GitHub Moon
===========

<img align="right" src="logo.png" alt="GitHub Moon Logo" width=160 border=10>

> Orbit GitHub repositories, download interesting artifacts, test
> them, and report the results back to the project via commit
> statuses.

This is useful in situations where you want to have a looser coupling
between a set of test rigs and a repository than a regular GitHub
workflow can provide. Rather than the repo having to know about all
available test rigs, _pulling_ in test results from them; any online
`ghmoon` can _push_ results to the repository.


Background
----------
`ghmoon` was created to manage physical test rigs for the [Infix][1]
OS.

Infix's default CI workflow will run its regression test suite on a
set of virtual nodes, using QEMU, which is a great way to catch most
regressions.

In the end though, the primary target for Infix is switches and
routers which, for performance, require offloading of as many flows as
possible to switching ASICs. Therefore, you have to run the tests on
real hardware to know that your offloading works as expected.

Real hardware costs real money, out of reach for the ragtag team that
is Kernel Kit. Instead, we rely on our users to host these systems and
provide us with the results. Using `ghmoon`, anyone looking to provide
results can simply request access to Infix via a personal access token
and start reporting.

> **NOTE**: Although Infix is `ghmoon`'s the raison d'être it can, in
> principle, be configured to orbit any repo.


Usage
-----

```
  ghmoon daemon [--publish]
    Continuously monitor repos for new matching artifacts, queue and process
	them. If --publish is specified, report progress via GitHub commit
	statuses, and publish a Gist of the full report.

  ghmoon process [--publish] <repo> <commit>
    Manually checkout <commit> from <repo>, then run the deploy, test, and
	report hooks for <repo>. If --publish is specified, report progress via
	GitHub commit statuses, and publish a Gist of the full report.

	NOTE: Ensure that no active daemon clashes with your manual processing job.
```


Installation
------------

To install `ghmoon` to be run by the current user's `systemd`
instance, run the provided install script:

    ./contrib/user-install.sh

Follow the instructions after the script exits.

If you are installing for a user that is not always logged in to the
system, you probably want to make sure that their `systemd` instance
is always started at system boot:

    sudo loginctl enable-linger <your-ghmoon-user>


Configuration
-------------
The following configuration orbits Infix, looks for `x86_64` builds,
and runs the default test suite on it.

```yaml
# The context is the string used to identify this moon. If not
# specified, it defaults to "user@hostname"
context: Jacky's laptop rig

repos:
  kernelkit/infix:
    # Each repo must define a jq(1) expression that is used to filter
    # out artifacts of interest based on the data returned by the
    # /repos/{owner]/{repo}/actions/artifacts endpoint.
    match: >-
      .workflow_run.head_repository_id == .workflow_run.repository_id
      and
      .name == "artifact-x86_64"

    # All hooks are run from the root directory from the repository.
    hooks:
      # The deploy hook should download the artifact, deploy it to
      # applicable nodes, and prepare the repository to run tests.
      deploy: |
        ./utils/gh-dl-artifact.sh $SHA

      # The test hook should, surprisingly, run the actual tests.
      test: |
        make O=x-gh-dl-$(echo $SHA | head -c8)-x86_64 test

      # By using the builtin report hook, we can just supply some extra
      # summary information via the hook below.
      report-test-summary: |
        tail -n+2 test/.log/last/result-gh.md
        echo
        echo **Exitcode**: $TEST_EXITCODE
```

[1]: https://github.com/kernelkit/infix
