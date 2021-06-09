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
            url: str,
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

            self.key = key
            self.state = state
            self.url = url
            self.name = name
            self.description = description

    class BuildContext:
        """A context for managing a build's status
        """

        def __init__(self, name: str, host: "BitBucket", commit: str) -> None:
            """Creates a new build context

            :param self:
                Self
            :param name:
                The name of the build
            :param host:
                The Git repository's host to update
            :param commit:
                The commit whose build status to manage

            :return none:
            """

            self._name = name
            self._host = host
            self._commit = commit

            self._status = None

        @property
        def status(self) -> bool:
            """Gets our build status

            :param self:
                Self

            :return bool:
                Our build status
            """

            return self._status

        @status.setter
        def status(self, status: bool) -> None:
            """Sets our build status

            :param self:
                Self
            :param status:
                The new status to set

            :return none:
            """

            self._status = status

        def start(self) -> bool:
            """Starts the build context

            :param self:
                Self

            :return True:
                Build context started
            :return False:
                Failed to start build context
            """

            if self._commit is None:
                return False

            return self._host.setBuildStatus(
                commit = self._commit,
                status = BitBucket.BuildStatus(
                    key = self._name,
                    state = BitBucket.BuildStatus.State.InProgress,
                    url = "none.com"
                )
            )

        def stop(self) -> bool:
            """Stops the build context

            :param self:
                Self

            :return True:
                Build context stopped
            :return False:
                Failed to stop build context
            """

            if self._commit is None:
                return False

            if self._status:
                state = BitBucket.BuildStatus.State.Successful
            else:
                state = BitBucket.BuildStatus.State.Failed

            return self._host.setBuildStatus(
                commit = self._commit,
                status = BitBucket.BuildStatus(
                    key = self._name,
                    state = state,
                    url = ""
                )
            )

        def __enter__(self) -> "BitBucket.BuildContext":
            """Enters the build context

            :param self:
                Self

            :return BuildContext:
                Us
            """

            self.start()

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

            self.stop()

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
