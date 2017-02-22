#!/usr/bin/python3

import xml.etree.ElementTree as ET
import sys, os, datetime, re
import getopt

nextCommentId = 1

def addPost(post, channel, username, wpUrl, doProtected, protectedPassword, doComments):
    if not doProtected and 'locked' in post.attrib and post.attrib['locked']:
        return
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = consolidateJoinedSpaces(post.find('title').text)
    ET.SubElement(item, 'link').text = 'https://' + username + '.livejournal.com/' + post.attrib['linkId'] + '.html'
    pubDate = datetime.datetime.strptime(post.get('date'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-6)))
    ET.SubElement(item, 'pubDate').text = pubDate.strftime('%a, %b %d %Y %H:%M:%S %z')
    ET.SubElement(item, 'dc:creator').text = username
    ET.SubElement(item, 'content:encoded').text = fixLJLinks(consolidateJoinedSpaces(post.find('body').text), username, wpUrl)
    ET.SubElement(item, 'wp:post_id').text = post.get('id')
    ET.SubElement(item, 'wp:post_date').text = pubDate.strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(item, 'wp:post_date_gmt').text = pubDate.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(item, 'wp:comment_status').text = 'open'
    ET.SubElement(item, 'wp:ping_status').text = 'open'
    safeTitle = post.find('title').text.strip().lower()
    permalink = re.sub('[^\s\w]', '', safeTitle)
    if safeTitle == '(no subject)':
        postName = post.get('linkId')
    else:
        postName = spacesToDashes(consolidateJoinedSpaces(permalink))
    ET.SubElement(item, 'wp:post_name').text = postName
    ET.SubElement(item, 'wp:status').text = 'publish'
    ET.SubElement(item, 'wp:post_parent').text = '0'
    ET.SubElement(item, 'wp:menu_order').text = '1'
    ET.SubElement(item, 'wp:post_type').text = 'post'
    if 'locked' in post.attrib and post.attrib['locked']:
        ET.SubElement(item, 'wp:post_password').text = protectedPassword
    else:
        ET.SubElement(item, 'wp:post_password').text = ''
    ET.SubElement(item, 'wp:is_sticky').text = '0'
    postTagsElem = post.find('tags')
    if postTagsElem:
        postTags = postTagsElem.findall('tag')
        for tag in postTags:
            tagElem = ET.SubElement(item, 'category', attrib={'domain': 'post_tag', 'nicename': tag.text.strip()})
            tagElem.text = tag.text.strip()
    if doComments:
        commentsElem = post.find('comments')
        if commentsElem:
            for comment in commentsElem.findall('comment'):
                appendComment(item, comment, 0, username, wpUrl)


def appendComment(item, ljComment, parentCommentId, username, wpUrl):
    global nextCommentId
    commentElem = ET.SubElement(item, 'wp:comment')
    thisCommentId = nextCommentId
    nextCommentId = nextCommentId + 1
    ET.SubElement(commentElem, 'wp:comment_id').text = str(thisCommentId)
    if 'username' in ljComment.attrib:
        ET.SubElement(commentElem, 'wp:comment_author').text = ljComment.attrib['username']
    ET.SubElement(commentElem, 'wp:comment_author_url')
    ET.SubElement(commentElem, 'wp:comment_author_IP')
    # ugh, this is in ISO 8601 format so the timezone has an extra ':' in it probably
    rawDate = ljComment.attrib['date']
    if rawDate[-3] == ':' and (rawDate[-6] == '-' or rawDate[-6] == '+'):
        rawDate = rawDate[:-3] + rawDate[-2:]
    pubDate = datetime.datetime.strptime(rawDate, '%Y-%m-%dT%H:%M:%S%z')
    ET.SubElement(commentElem, 'wp:comment_date').text = pubDate.strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(commentElem, 'wp:comment_date_gmt').text = pubDate.strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(commentElem, 'wp:comment_content').text = fixLJLinks(consolidateJoinedSpaces(ljComment.find('body').text), username, wpUrl)
    ET.SubElement(commentElem, 'wp:comment_approved').text = '1'
    ET.SubElement(commentElem, 'wp:comment_type')
    ET.SubElement(commentElem, 'wp:comment_parent').text = str(parentCommentId)
    if ('username' in ljComment and ljComment.attrib['username'] == username):
        ET.SubElement(commentElem, 'wp:comment_user_id').text = '1'
    repliesElem = ljComment.find('replies')
    if repliesElem:
        for reply in repliesElem.findall('comment'):
            appendComment(item, reply, thisCommentId, username, wpUrl)


def main(inFile, outFile, options):
    #print(inFile)
    #print(outFile)
    tree = ET.parse(inFile)
    root = tree.getroot()
    posts = root.findall('post')

    ns = {'excerpt': 'http://wordpress.org/export/1.2/excerpt/', 'content': 'http://purl.org/rss/1.0/modules/content/', 'wfw': 'http://purl.org/rss/1.0/modules/content/', 'dc': 'http://purl.org/dc/elements/1.1/', 'wp': 'http://purl.org/dc/elements/1.1/'}
    rss = ET.Element('rss', {'version': '2.0'})
    for nsKey in ns:
        ET.register_namespace(nsKey, ns[nsKey])
        rss.attrib['xmlns:' + nsKey] = ns[nsKey]
    username = root.attrib['username']
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = username + "'s LiveJournal"
    ET.SubElement(channel, 'wp:wxr_version').text = '1.2'
    authorElem = ET.SubElement(channel, 'wp:author')
    ET.SubElement(authorElem, 'wp:author_id').text = '1'
    ET.SubElement(authorElem, 'wp:author_login').text = username
    ET.SubElement(authorElem, 'wp:author_display_name').text = username

    for post in posts:
        #if post.attrib['linkId'] == '428874': # lots of nested comments
        #if post.attrib['linkId'] == '493396': # protected
        #if post.attrib['linkId'] == '179819': # lj-user link
        #if post.attrib['linkId'] == '179387': # lj-cut
            addPost(post, channel, username, options['wpUrl'], options['protected'], options['protectedPassword'], options['comments'])

    outRoot = ET.ElementTree(rss)
    indent(rss)
    outRoot.write(outFile, encoding='UTF-8', xml_declaration=True)
    #ET.dump(outRoot)

def spacesToDashes(d):
    return d.replace(' ', '-')

def consolidateJoinedSpaces(s):
    # https://stackoverflow.com/questions/2077897/substitute-multiple-whitespace-with-single-whitespace-in-python
    return ' '.join(s.split())

def fixLJLinks(s, ljUsername, wpUrl):
    s = re.sub(r'a href="https?://' + ljUsername + '.livejournal.com/(\d+).html"', r'a href="' + wpUrl + r'\1/"', s)
    s = re.sub(r'<lj user="([^"]+)"/?>', r'<a href="https://\1.livejournal.com"><b>\1</b></a>', s)
    return s


# http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def usage():
    print("Usage")
    print('-h  help')
    print('-i <filename>/--input=  input allPosts.xml file')
    print('-o <filename>/--output=  output XML file')
    print('-w <url>/--wpUrl=  URL of your WordPress site (for fixing up links to it)')
    print('-p <password>/--protectedPassword=  Password to use for protected LJ posts')
    print('-n /--noProtectedPosts  Do not export any protected LJ posts')
    print('-c /--noComments  Do not export any comments')

if (__name__ == '__main__'):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:w:p:nc", ["help", 'input=', 'output=', 'wpUrl=', 'protectedPassword=', 'noProtectedPosts', 'noComments'])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    options = {'protected': True, 'comments': True}
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-i', '--input'):
            options['input'] = a
        elif o in ('-o', '--output'):
            options['output'] = a
        elif o in ('-p', '--protectedPassword'):
            options['protectedPassword'] = a
        elif o in ('-w', '--wpUrl'):
            options['wpUrl'] = a
            if (options['wpUrl'] != '' and not options['wpUrl'].endswith('/')):
                options['wpUrl'] = options['wpUrl'] + '/'
        elif o in ('-n', '--noProtectedPosts'):
            options['protected'] = False
        elif o in ('-c', '--noComments'):
            options['comments'] = False

    if 'input' not in options:
        print("No input specified!")
        usage()
        sys.exit(2)
    if 'output' not in options:
        print("No output specified!")
        usage()
        sys.exit(2)
    if 'wpUrl' not in options:
        print("No WordPress URL specified!")
        usage()
        sys.exit(2)
    if not (options['wpUrl'] == '' or options['wpUrl'].startswith('http://') or options['wpUrl'].startswith('https://')):
        print("WordPress URL must be empty or start with http:// or https://")
        usage()
        sys.exit(2)
    if options['protected']:
        if 'protectedPassword' not in options:
            print("No protected password specified! Either specify one or use -n to not export protected posts")
            usage()
            sys.exit(2)
    else:
        if 'protectedPassword' in options:
            print("Protected password specified, but we are not exporting protected posts!")
            usage()
            sys.exit(2)
        options['protectedPassword'] = 'jslkdfjqwlkjalskdjflqwkjerlkjasdflkjasdlkfjasdflkasdjf' # We won't actually use this, but just in case....

    main(options['input'], options['output'], options)
