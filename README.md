# Bothermione Flask

The 2023 version of the Bothermione flask container now uses Playwright to simulate browser activity as opposed to bot requests in order to lower potential of slowdowns/blockages.

To run your own Heroku version, deploy using a container stack to ensure the Dockerfile is used to install. This is required to ensure chromium is available.
