#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web

from blackpearl.black_pearl_request import BlackPearlRequestHandler
from blackpearl.black_pearl_response import Response

from pollens.client import pl_client
from pollens.client.Pollens.ttypes import *
from honeycomb.client import hc_client

from app_error import AppConstants


c_hc=hc_client.HoneycombClient()
c_hc.connect('127.0.0.1', 9001)

c_pl=pl_client.PollensClient()
c_pl.connect('127.0.0.1', 9000)


class test(BlackPearlRequestHandler):
    def echo(self, message={'type':str, 'required':True}):
        return Response(result={'hey':"%s" % message})

    def age(self, age={'type':int, 'required':True}):
        return Response(result={'age':age})

    def getPiecesList(self):
        user = c_hc.getUser(user_id=1)
        piece_ids = list(xrange(100))
        pieces = c_pl.getPieces(piece_ids=piece_ids)

        results = []
        for i in pieces:
            print i.targets[0]
            owner = c_hc.getUser(i.owner_id)
            # OK, compose piece item
            item = {}
            item['url'] = i.targets[0].url
            item['owner'] = owner.nick_name
            item['owner_id'] = owner.id
            results.append(item)
        return Response(result=results)

    def piece(self, id={'type':int, 'required':True}):
        """
        piece, owner, heart-ers, tags(#love, #travel)
        """
        piece_id = id
        try:
            result = {}
            piece = c_pl.getPiece(piece_id)
            result['targets'] = [ {'url':i.url, 'motion':i.motion} for i in piece.targets ]

            # get owner
            try:
                owner = c_hc.getUser(piece.owner_id)
            except Exception as e:
                print "[WARNING] exc occurs while get owner:%s of piece:%s caz:%s" % (piece.owner_id, piece_id, e)
                # TODO Thu Jun 25 15:17:59 2015 [fatal error, ResponseCode]
            result['owner'] = { 'avatar':owner.avatar, 'name':owner.nick_name, 'id':owner.id }

            # get heart-ers
            result['hearters'] = hearters = []
            for i in piece.follower_ids:
                try:
                    u = c_hc.getUser(i)
                except Exception as e:
                    print "[WARNING] exc occurs while get user:%s, caz:%s" % (piece.owner_id, e)
                    continue
                h = { 'avatar':u.avatar, 'name':u.nick_name, 'id':u.id }
                hearters.append( h )

            # brief
            result['brief'] = piece.brief
            # [TODO] get tags
            return Response(result=result)
        except TIOError as e:
            print 'TIOError', e
            return Response(AppConstants.RC_FAILED_GET_PIECE, why=e._message)
        except TIllegalArgument as e:
            print 'TIllegalArgument', e
            return Response(AppConstants.RC_FAILED_GET_PIECE, why=e._message)
        except TApiError as e:
            print 'TApiError', e
            return Response(AppConstants.RC_FAILED_GET_PIECE, why=e._message)

        def follow(self, session_id={'type':(int,long), 'required':True},
                   follow_infos={'type':str, 'required':True} ):
            """follow_infos format:
            item = 'target_type:target_id'
            follow_infos = item[$item...]

            eg:

            'piece:1$piece:2$album:2$user:20'
            """
            # TODO Thu Jun 25 22:15:55 2015 []
            # get follower_id by session_id from session
            # CALL FOLLOW METHOD.
            pass

        
