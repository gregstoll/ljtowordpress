# ljtowordpress
Script to convert a LiveJournal dump made by [LJBackup](https://gregstoll.com/ljbackup/) to a WordPress-friendly file that can be imported.  For more information, see [the project homepage](https://gregstoll.com/ljbackup/ljtowordpress/) as well as [this thread on the WordPress forums](https://en.forums.wordpress.com/topic/import-from-livejournal).

This script was created at a time when the WordPress import from LiveJournal was not working - if that's working, you should probably use that instead as it's likely to be better supported.

##What does it do?
* Preserves post titles, dates, and content
* Can optionally import protected posts from LJ and set a password on them in WordPress.
* Keeps a similar URL scheme, so a link to http://gregstoll.wordpress.com/495263 will bring up the post originally made at http://gregstoll.livejournal.com/495263.html
* Fixes links to other LJ entries in your journal to point to the corresponding WordPress entry
* Preserves comment bodies, including nesting
* Preserves tags
* Turns `<lj-user>` tags into a link to that user's LiveJournal

##What does it not do?
* Does not preserve mood, music, or location
* Does not copy anything else from your journal other than posts (i.e. no blog title, global links, etc)
* Does preserve the name of the author of comments, but if it's anyone other than the journal author it makes no attempt to set the author's URL, etc
* `<lj-cut>` tags don't get displayed, although their content is displayed
* Does not set any excerpts for posts
* Does not preserve userpic or any images you have stored on LJ
* Does not preserve the author of posts (all will be set to the owner of the journal), so this probably won't work well with communities
* Does not convert `<lj-embed>` tags

##Caveats
The way LJ formats posts is a little weird, which doesn't play nice with some WordPress themes. For example, the Franklin theme has weird spacing for `<br>`'s.

##How to use this
1. Use [LJBackup](https://gregstoll.com/ljbackup/) to make a backup of your LiveJournal
2. Unzip file to a folder on your computer
3. Move `allPostsToWordpress.py` to the same directory as `allPosts.xml`
4. In order to run this script, you need to have [Python 3](https://www.python.org/) installed
5. Starting on line 135 of `allPostsToWordpress.py`, you'll see the arguments that can be used. Choose one of the following formats (and customize for your files as needed):
    * `python3 allPostsToWordpress.py -i allPosts.xml -o wordpress.xml -w "" -n`
    * `python3 allPostsToWordpress.py --input=allPosts.xml --output=wordpress.xml --wpUrl='' --noProtectedPosts` 
6. In the above command of your choice, name the `.xml` file to whatever you want or keep it as `wordpress.xml`
7. Run the command in the terminal of your choice and it'll go through your Livejournal to export everything to `wordpress.xml`
8. Once completed, in your WordPress installation, go to the Dashboard and look for `Tools > Import`
9. Choose `Install Now` under the WordPress importer
10. Click Start Import, then click on the cloud icon and select the WordPress XML file
11. Click through a few more times, then wait a while :-)
12. All your posts should now be in your WordPress installation
