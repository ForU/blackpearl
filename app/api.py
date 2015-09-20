#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web

from blackpearl.black_pearl_request import BlackPearlRequestHandler
from blackpearl.black_pearl_response import Response

from pollens.client import pl_client
from pollens.client.Pollens.ttypes import *
from honeycomb.client import hc_client
from honeycomb.client.Honeycomb.ttypes import *
from honeycomb.client.common.hc_constants import CommonConstants as HcCommonConstants

from app_error import AppConstants


c_hc=hc_client.HoneycombClient()
c_hc.connect('127.0.0.1', 9001)

c_pl=pl_client.PollensClient()
c_pl.connect('127.0.0.1', 9000)


class user(BlackPearlRequestHandler):
    def home(self, uid={'type':int,'required':True}):
        # TODO Fri Jul 17 14:28:55 2015 []
        # check exists first

        # user, pieces, albums, followers, following
        user = c_hc.getUser(uid)
        pieces_total, pieces = c_pl.getPiecesTotalOfOwner(uid), c_pl.getPiecesOfOwner(uid)
        albums_total, albums = c_pl.getAlbumsTotalOfOwner(uid), c_pl.getAlbumsOfOwner(uid)
        followers = c_hc.getUserFollowRelationship(hc_client.CommonConstants.FOLLOW_MODE_FOLLOWER, uid)
        following = c_hc.getUserFollowRelationship(hc_client.CommonConstants.FOLLOW_MODE_FOLLOWING, uid)

        # refine pieces
        for i in pieces:
            i.targets = [item.__dict__ for item in i.targets]

        # compose data
        ret = {
            'user': user.__dict__,
            'pieces': {'total':pieces_total, 'contents':[i.__dict__ for i in pieces]},
            'albums': {'total':albums_total, 'contents':[i.__dict__ for i in albums]},
            'followers': {'total': followers.total, 'contents':[i.__dict__ for i in followers.users]},
            'following': {'total': following.total, 'contents':[i.__dict__ for i in following.users]},
        }
        return Response(result=ret)

    def me(self, uid={'type':int,'required':True}):
        pass


class common(BlackPearlRequestHandler):

    # def pieces(self, user_id={'type':int, 'required':True},
    #            page={'type':int, 'default':1},
    #            n={'type':int, 'default':10}):
    #     # TODO Wed Jul  8 09:56:27 2015 []
    #     """
    #     @user_id: id of user
    #     @page: page index
    #     @n: maybe we should hide this
    #     """
    #     user = c_hc.getUser(user_id=1)
    #     piece_ids = list(xrange(100))
    #     pieces = c_pl.getPieces(piece_ids=piece_ids)
    #     # import ipdb; ipdb.set_trace()

    #     results = []
    #     for i in pieces.pieces:
    #         print i.targets[0]
    #         owner = c_hc.getUser(i.owner_id)
    #         # OK, compose piece item
    #         item = {}
    #         item['url'] = i.targets[0].url
    #         item['owner'] = owner.nick_name
    #         item['owner_id'] = owner.id
    #         results.append(item)
    #     return Response(result=results)

    def piece(self, id={'type':int, 'required':True}):
        """detail"""
        piece_id = id
        try:
            piece = c_pl.getPiece(piece_id)
        except Exception as e:
            return Response(AppConstants.RC_FAILED_GET_PIECE, why=str(e))

        # handle piece's attributes
        piece_detail = {}
        piece_detail['cover'] = piece.cover
        piece_detail['name'] = piece.name
        piece_detail['domain'] = piece.domain
        piece_detail['price'] = piece.price
        piece_detail['price_unit'] = 'rmb'
        piece_detail['origin_price'] = piece.origin_price
        piece_detail['brief'] = piece.brief

        # lovers, collectors (only count)
        plovers = c_pl.getPieceLovers(piece_id, 0, 0)
        piece_detail['lovers_total'] = plovers.total

        # piece.owner(other than colloctors)
        try:
            owner = c_hc.getUser(piece.owner_id)
        except Exception as e:
            return Response(AppConstants.RC_FAILED_GET_PIECE, why=str(e))

        powner = {}
        powner['id'] = owner.id
        powner['nick_name'] = owner.nick_name
        powner['avatar'] = owner.avatar

        piece_detail['owner'] = powner

        # owner's album contains this piece

        return Response(result=piece_detail)

    def follow(self,
               session_id={'type':long, 'required':True},
               desc={'type':str, 'required':True} ):

        """follow_infos format:
        item = 'target_type:target_id'
        follow_infos = item[$item...]

        eg:

        'p:1:1$p:2:1$a:2$u:20'
        """
        # TODO Thu Jul  2 16:18:42 2015 [get follower_id from session by @session_id]
        follower_id = int(session_id)
        items = desc.split('$')
        hc_follows = []
        for item in items:
            item = item.split(':')
            print item
            item_type = item[0]
            if item_type == 'p':
                if len(item) < 3:
                    print "ERROR: invalid item:%s" % item
                    continue
                c_pl.followPiece(follower_id=follower_id, piece_id=int(item[1]), album_id=int(item[2]))
            elif item_type == 'a':
                if len(item) < 2:
                    print "ERROR: invalid item:%s" % item
                    continue
                c_pl.followAlbum(follower_id=follower_id, album_id=int(item[1]))

            elif item_type == 'u':
                if len(item) < 2:
                    print "ERROR: invalid item:%s" % item
                    continue
                fi = FollowInfo(target_type=HcCommonConstants.FOLLOW_TARGET_TYPE_USER, target_id=int(item[1]))
                hc_follows.append(fi)
        if hc_follows:
            c_hc.follow(follower_id, hc_follows)
        return Response(AppConstants.RC_SUCCESS)
