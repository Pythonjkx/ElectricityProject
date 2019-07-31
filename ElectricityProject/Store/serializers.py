from rest_framework import serializers
from Store.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    # 声明数据
    class Meta:
        model = Goods #要进行接口序列化的模型
        fields = ['goods_name','goods_price','goods_number','id','goods_date','goods_safeDate']#序列要返回的字段


class GoodsTypeSerializer(serializers.HyperlinkedModelSerializer):
    # 声明查询的表和返回的字段
    class Meta:
        model = GoodsType
        fields = ['name','description']