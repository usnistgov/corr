<p align="center">
    <img src="https://rawgit.com/usnistgov/corr/master/corr-view/frontend/images/logo.svg"
         height="240"
         alt="CoRR logo"
         class="inline"/>
</p>

<p align="center">
<a href="https://corr.nist.gov" target="_blank">
<img src="https://img.shields.io/badge/corr-nist-cyan.svg"
alt="CoRR NIST Public Instance">
</a>
<a href="https://corrworkspace.slack.com" target="_blank">
<img src="https://img.shields.io/badge/corr-slack-purple.svg"
alt="Slack">
</a>
<a href="http://corr.readthedocs.io/en/latest/?badge=latest" target="_blank">
<img src="https://readthedocs.org/projects/corr/badge/?version=0.2" alt="Reathedocs">
</a>
<a href="https://www.youtube.com/playlist?list=PLiWY1GXAXKFk4aSwI9CfyAoDwR6bjD8zV">
<img src="https://img.shields.io/badge/corr-youtube-red.svg" alt="Youtube Playlist" height="18">
</a>
<a href="https://github.com/usnistgov/corr/blob/master/LICENSE">
<img src="https://img.shields.io/badge/license-mit-blue.svg" alt="License" height="18">
</a>
</p>

# Introduction

Before going further, you must have access to a running instance of CoRR. Please refer to
[How to launch one](./LAUNCH.md) if you are a administrator or contact your administrator to do so.
Once you have an instance you can proceed as an Administrator or a User. Read the section that is suited to your role.
A CoRR instance can be accessed in two ways. A web way with a browser and a api way with a supported and authorized
tool credentials on the instance.

# Adminstrator

After launching an instance, use the credential provided in the setup section. If you don't remember it, you will find it
in credentials/tmp_admin.json. We recommend changing it in the platform after the first login. To have information on the parts
of the platform and how to administer it, refer to our youtube videos provide in the badge above. An administrator is reponsible
for the instance moderation (approve new user registration, increase user quota, lock down accounts, etc..), content moderation
(project, environments, records, diffs and any other content modification and deletion). Finally an administrator is responsible
for managing support for execution management tools by creating credentials for each one he/she want to support. Please refer to
the administration video in the CoRR administration youtube videos playlist.

# Users

To access a CoRR instance, a user must first register. Upon registration, the user must inform the instance administrator to
approve the account before login is granted. In a non-moderated on registration instance, the user is logged in automatically upon
registration. Once logged in, the user is recommended to watch the CoRR user youtube videos playlist to be introduced into how to
navigate and use the instance.

# Tools and Security

Tools are integration credentials created by an instance admin to allow users to push content under a specific
execution management tool scope/content. To be able to push content with a tool, a user will be required to provide its
api key and the the tool api key. The administrator may recycle tools api keys for security reasons. Without a user api key
and the right tool api key on the instance all communication to the CoRR instance will be rejected. Please refer to the tools
video in the CoRR youtube videos playlist. After more than 30 minutes of inactivity, the user is automatically logged out.
Moreover, after 3 trials failures of login with a wrong password, the user account is placed on lockdown mode. Contact your
instance administrator to be re-approved and be provided a temporary password. Refer to the CoRR security youtube videos playlist.

# Important Note

Regarding user moderation, CoRR can be configured to login user automatically after registration, this is an advanced configuration
that can be handled by the administrator. Other security consideration will require advanced configuration that can only be performed
by the admin.
