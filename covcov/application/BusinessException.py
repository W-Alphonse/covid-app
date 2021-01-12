

class BusinessException(Exception):

  def __init__(self, context:dict, *args, **kwargs):
    super(*args, **kwargs)
    self.context = context