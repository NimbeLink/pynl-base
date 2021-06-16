"""
Tools for working with BitBucket

(C) NimbeLink Corp. 2020

All rights reserved except as explicitly granted in the license agreement
between NimbeLink Corp. and the designated licensee. No other use or disclosure
of this software is permitted. Portions of this software may be subject to third
party license terms as specified in this software, and such portions are
excluded from the preceding copyright notice of NimbeLink Corp.
"""

import requests

from .host import Host

class BitBucket(Host):
    """A BitBucket Git repository host
    """

    BaseUrl = "git@bitbucket.org:nimbelink"
    """The base repository URL"""

    RestApiUrl = "https://api.bitbucket.org/2.0/repositories/nimbelink"
    """The base REST API URL"""

    class BuildStatus:
        """Build statuses we can set
        """

        class State:
            """The various states the build can be in
            """

            InProgress  = "INPROGRESS"
            Successful  = "SUCCESSFUL"
            Failed      = "FAILED"

        def __init__(
            self,
            key: str,
            state: str,
            url: str = None,
            name: str = None,
            description: str = None
        ) -> None:
            """Creates a new build status

            :param self:
                Self
            :param key:
                The key for this build
            :param state:
                The new state of the build step
            :param url:
                A URL for this build
            :param name:
                The name of the step being performed
            :param description:
                The description of this build

            :return none:
            """

            # A URL is required by BitBucket
            if url is None:
                url = "none.com"

            self.key = key
            self.state = state
            self.url = url
            self.name = name
            self.description = description

    class BuildContext:
        """A context for managing a build's status
        """

        def __init__(self, host: "BitBucket", commit: str, buildId: str) -> None:
            """Creates a new build context

            :param self:
                Self
            :param host:
                The Git repository's host to update
            :param commit:
                The commit whose build status to manage
            :param buildId:
                The ID of the build

            :return none:
            """

            self._host = host
            self._commit = commit
            self._buildId = buildId

            self._steps = {}

        def setState(self, name: str, state: "BitBucket.BuildStatus.State") -> None:
            """Sets our build status

            :param self:
                Self
            :param name:
                The name of the build step
            :param state:
                The new state to set

            :return none:
            """

            updated = self._host.setBuildStatus(
                commit = self._commit,
                status = BitBucket.BuildStatus(
                    key = name,
                    state = state,
                    description = self._buildId
                )
            )

            # If the build was updated, note the state we updated to
            if updated:
                self._steps[name] = state

        def setInProgress(self, name: str) -> None:
            """Sets a build status to 'in progress'

            :param self:
                Self
            :param name:
                The name of the build step

            :return none:
            """

            return self.setState(name = name, state = BitBucket.BuildStatus.State.InProgress)

        def setSuccess(self, name: str) -> None:
            """Sets a build status to 'successful'

            :param self:
                Self
            :param name:
                The name of the build step

            :return none:
            """

            return self.setState(name = name, state = BitBucket.BuildStatus.State.Successful)

        def setFailed(self, name: str) -> None:
            """Sets a build status to 'failed'

            :param self:
                Self
            :param name:
                The name of the build step

            :return none:
            """

            return self.setState(name = name, state = BitBucket.BuildStatus.State.Failed)

        def __enter__(self) -> "BitBucket.BuildContext":
            """Enters the build context

            :param self:
                Self

            :return BuildContext:
                Us
            """

            return self

        def __exit__(self, type, value, traceback) -> None:
            """Exits the build context

            :param self:
                Self
            :param type:
                The type of exception, if any
            :param value:
                The value of the exception, if any
            :param traceback:
                The traceback of the exception, if any

            :return none:
            """

            for name, state in self._steps.items():
                # If this step was resolved, nothing to do for it
                if ((state == BitBucket.BuildStatus.State.Successful) or
                    (state == BitBucket.BuildStatus.State.Failed)
                ):
                    continue

                # We must have ended prematurely, so update the status with a
                # failure
                #
                # We'll technically be updating the dictionary element we're
                # currently examining, but that's fine.
                self.setFailed(name = name)

    @property
    def url(self) -> str:
        """Gets the repository's URL

        :param self:
            Self

        :return str:
            The repository's URL
        """

        return "{}/{}.git".format(BitBucket.BaseUrl, self.name)

    def setBuildStatus(self, commit: str, status: "BitBucket.BuildStatus") -> bool:
        """Sets the build status for a commit

        :param self:
            Self
        :param commit:
            The Git commit whose build status to update
        :param status:
            The build status to set

        :return True:
            Build status set
        :return False:
            Failed to set build status
        """

        # If we don't have credentials, we won't be able to authenticate our
        # REST API call
        if self.credentials is None:
            return False

        # Make the data for the new build status
        data = {
            "key":          status.key,
            "state":        status.state,
            "url":          status.url
        }

        if status.name is not None:
            data["name"] = status.name

        if status.description is not None:
            data["description"] = status.description

        # Make the REST API URL we'll post to
        apiUrl = ("{}/{}/commit/{}/statuses/build".format(
            BitBucket.RestApiUrl,
            self.name,
            commit
        ))

        # Make our credentials
        auth = (self.credentials.username, self.credentials.password)

        # Post!
        response = requests.post(apiUrl, auth = auth, json = data)

        return response.ok

    def getBuildContext(self, commit: str, buildId: str) -> "BitBucket.BuildContext":
        """Gets a new build context for a commit

        :param self:
            Self
        :param commit:
            The commit to get a context for
        :param buildId:
            The build ID for the commit

        :return BitBucket.BuildContext:
            The build context
        """

        return BitBucket.BuildContext(host = self, commit = commit, buildId = buildId)
