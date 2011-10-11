#!/usr/local/bin/python

import sys
import re
from BeautifulSoup import BeautifulSoup
from collections import namedtuple

join_date_regex = re.compile('Join Date: (\S+) (\d{4})')
location_regex = re.compile('Location: (.*)')
posts_regex = re.compile('Posts: (\S+)')
user_id_regex = re.compile('http://forums.pelicanparts.com/members/(\d+)\.html')

Comment = namedtuple('Comment', 'text sig')
User = namedtuple('User', 'name join_month join_year location number_posts user_id')

def parse_comment(post):
	try:
		b = post.findAll('td', { 'class' : 'alt1' } )[0]
		comment_parts = b.findAll('div')
		text = ''
		if len(comment_parts) == 1:
			return Comment(comment_parts[0].text, None)
		for cp in comment_parts[:-1]:
			text += '; ' + cp.text
		return Comment(text,comment_parts[-1].text)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		return None


def parse_user(post):
	username_parts = post.findAll('td', { "align" : "left" })
	if not username_parts:
		return
	username = username_parts[0].text
	join_month = None
	join_year = None
	location = None
	number_posts = None
	for user_facts in post.findAll('div', { "class" : "smallfont" } ):
		for line in user_facts:
			text = None
			try:
				text = line.text
			except:
				continue
			if not join_month:
				m=join_date_regex.search(text)
				if m:
					join_month = m.group(1)
					join_year = int(m.group(2))
			if not location:
				m=location_regex.search(text)
				if m:
					location = m.group(1)
			if not number_posts:
				m=posts_regex.search(text)
				if m:
					number_posts = int(m.group(1).replace(',', ''))
	user_name_line = post.findAll('a', { 'class' : 'bigusername' } )[0]
	user_link = [y for y in user_name_line.attrs if y[0] == 'href'][0][1]
	m = user_id_regex.search(user_link)
	return User(username, join_month, join_year, location, number_posts, int(m.group(1)))


def main(args):
	f = open(args[0])
	html = f.read()
	soup = BeautifulSoup(html)
	p=soup.findAll("div", { "class" : "page" })
	print "<html><head><title>Parsing for", f.name, "</title></head><body>";
	print "<table border='thin'>"
	for t in p[2:-1]:
		user = parse_user(t)
		comment = parse_comment(t)
		print "<tr><td><ul>"
		print "<li>", user.name, "</li><li>", user.join_month, user.join_year, "</li><li>", user.location, "</li><li>", user.number_posts, "</li><li>", user.user_id, "</li>"
		print "</ul></td><td>"
		print comment.text
		if comment.sig:
			print "<br/>", comment.sig
		print "</td></tr>"
	print "</table></body></html>"


if __name__ == "__main__":
	main(sys.argv[1:])
