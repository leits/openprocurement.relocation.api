# -*- coding: utf-8 -*-
from openprocurement.api.utils import generate_id
from openprocurement.relocation.api.validation import validate_transfer_data
from openprocurement.relocation.api.utils import (
    transferresource, save_transfer, set_ownership
)
from openprocurement.api.utils import json_view, context_unpack, APIResource


@transferresource(name='Transfers',
                  path='/transfers/{transfer_id}',
                  collection_path='/transfers',
                  description="Transfers")
class TransferResource(APIResource):
    """ Resource handler for Transfers """

    @json_view(permission='view_transfer')
    def get(self):
        return {'data': self.request.validated['transfer'].serialize("view")}

    @json_view(content_type="application/json", permission='create_transfer',
               validators=(validate_transfer_data,))
    def collection_post(self):
        transfer = self.request.validated['transfer']

        access_token = generate_id()
        transfer_token = generate_id()
        set_ownership(transfer, self.request, access_token=access_token,
                      transfer_token=transfer_token)

        self.request.validated['transfer'] = transfer
        self.request.validated['transfer_src'] = {}
        if save_transfer(self.request):
            self.LOGGER.info('Created transfer {}'.format(transfer.id),
                             extra=context_unpack(
                                 self.request,
                                 {'MESSAGE_ID': 'transfer_create'},
                                 {'transfer_id': transfer.id}))
            self.request.response.status = 201
            return {
                'data': transfer.serialize("view"),
                'access': {
                    'token': access_token,
                    'transfer': transfer_token,
                }
            }
