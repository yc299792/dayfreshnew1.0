from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls,**initkwargs):
        # 调用view的as_view方法
        view = super(LoginRequiredMixin,cls).as_view(**initkwargs)
        return login_required(view)
