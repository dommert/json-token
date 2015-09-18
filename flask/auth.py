class APIKeyAuthentication(Authentication):
    """
    Requires a model that has at least two fields, "key" and "secret", which will
    be searched for when authing a request.
    """
    key_field = 'key'
    secret_field = 'secret'

    def __init__(self, auth, model, protected_methods=None):
        super(APIKeyAuthentication, self).__init__(protected_methods)
        self.model = model
        self._key_field = model._meta.fields[self.key_field]
        self._secret_field = model._meta.fields[self.secret_field]

    def get_query(self):
        return self.model.select()

    def get_key(self, k, s):
        try:
            return self.get_query().where(
                self._key_field==k,
                self._secret_field==s
            ).get()
        except self.model.DoesNotExist:
            pass

    def get_key_secret(self):
        for search in [request.headers, request.args, request.form]:
            if 'key' in search and 'secret' in search:
                return search['key'], search['secret']
        return None, None

    def authorize(self):
        if request.method not in self.protected_methods:
            return True

        key, secret = self.get_key_secret()
        try:
            g.user = User.select().join(APIKey).where(APIKey.key == key, APIKey.secret == secret).get()
            return g.user
        except User.DoesNotExist:
            return False
