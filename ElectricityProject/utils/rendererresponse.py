from rest_framework.renderers import JSONRenderer

class Customrenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):

        if renderer_context:
            if isinstance(data,dict):
                msg = data.pop('msg','请求失败')
                code = data.pop('code',0)
            else:
                msg = '请求失败'
                code = 0
            ret = {
                'msg':msg,
                'code':code,
                'author':'贾宽新很帅',
                'data':data
            }
            return super().render(ret,accepted_media_type,renderer_context)
        else:
            return super().render(data,accepted_media_type,renderer_context)