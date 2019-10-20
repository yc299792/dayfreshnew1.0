from django.db import models

class BaseModel(models.Model):
    """模型抽象基类"""
    create_time = models.DateField(auto_now=True,verbose_name='创建时间')
    update_time = models.DateField(auto_now=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        """抽象模型类"""
        abstract = True
