## HowTo Operate a GH Moon

> [!IMPORTANT]
> When you are done, remember to flush the queue and restart the moon!

### Accessing the Test Environment

Before working with DUTs, you'll need access to the test server.  Check
with your team for the correct server address and credentials.  A server
may host multiple moons, one for each test system, here we assume the
`styx` moon, which has console ports with the same name.

 1. When logged in, change to the moon user:

        sudo machinectl shell --uid styx

 2. Check if moon is running a job already:
 
        systemctl --user status ghmoon.service

 3. Stop the moon user:

        systemctl --user stop ghmoon.service


### Working with Multiple DUTs

When debugging across multiple devices, you'll need console access to
monitor their behavior:

 1. From your user account, connect to the DUT consoles:
 
        console styx1 ... styx4

 2. Each DUT needs a proper boot image.  Set up `rootfs.itb` links in
    `/srv/bootfile-styxN`
 3. Verify connectivity to all DUTs before proceeding with tests

> [!TIP]
> Start with `byobu` - it's excellent for managing multiple console
> sessions and comes pre-configured on the test systems.  Many use
> TTY 0 as the "control channel", either for restarting DUTs or to
> run tests (from `make test-sh`), and TTY 1 .. 4 for each of the
> console sessions.


### Test Environment Setup

To prepare for testing:

 1. Get your development branch and test artifact:
    - Either build locally
    - Or use `utils/gh-dl-artifact.sh` to fetch a specific build

 2. Set up your test shell, e.g., in `byobu` window 0:

        cd test/
        make TEST_MODE=host TOPOLOGY=/etc/infamy-styx.dot test-sh

 3. Open separate console windows for each DUT you need:

        console styx1    # In byobu window 1
        console styx2    # In byobu window 2
        # etc...

From here, follow the test procedures in testing.md. 


### Cleaning Up

When finished debugging or testing:

 1. Restore the moon service:

        systemctl --user start ghmoon.service 

 2. If the moon was down for a while, clean up the queue:

        ghmoon enqueue
        mv .ghmoon/workqueue/todo/* .ghmoon/workqueue/done/
        systemctl --user start ghmoon.service
