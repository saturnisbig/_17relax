#!/usr/bin/env python
# _*_ coding: utf-8 _*_


def urllib_error(e):
    if hasattr(e, 'reason'):
        print "Failed to reach the server"
        print "The reason: ", e.reason
    elif hasattr(e, 'code'):
        print "The server couldn't fulfill the request"
        print "Error code: ", e.code
        print "Return content: ", e.read()
