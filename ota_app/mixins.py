# # hotel ownership mixin
#
# class HotelOwnershipMixin(object):
#
#     def dispatch(self, request, *args, **kwargs):
#         hid = kwargs['hid']
#         hotel = Hotel.objects.get(id=hid)
#         hotel_owner_username = hotel.hotel_owner.user.username
#         if hotel_owner_username == request.user.username:
#             return super().dispatch(request, *args, **kwargs)
#         else:
#             raise('PermissionDenied')