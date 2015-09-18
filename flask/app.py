
# Model
class APIKey(db.Model):
    key = CharField()
    secret = CharField()
    user = ForeignKeyField(User)
    
# Controller
@app.route('/login', methods=['POST'])
def login():
    try:
        key = request.json["key"]
        secret = request.json["secret"]
        print "Key and secret delivered"
        try:
            user = User.select().join(APIKey).where(APIKey.key == key, APIKey.secret == secret).get()
            print "APIKey found"
            return jsonify ({"success" : True, "user_id" : user.id})
        except: #key and secret were invalid
            print "Key and secret invalid"
            return jsonify({"success" : False, "reason" : "key invalid"})
    except KeyError: # no key delivered, check for any existing keys for the user, if not, create one
        try: #check whether a username and password were delivered
            username = request.json["username"]
            password = request.json["password"]
            print "Username and password found"
            user = User.get(User.username == username)
            print "Username exists"
            if user.check_password(password): #if the user exists and the password is correct
                print "Password correct"
                key = urandom(50).encode('hex')
                secret = urandom(50).encode('hex')
                key_secret = APIKey.get_or_create(key = key, secret = secret, user = user)
                return jsonify ({"success" : True, "user_id" : user.id, "key" : key, "secret" : secret})
            else: #the user exists, but the password is incorrect
                return jsonify ({"success" : False, "reason" : "Password incorrect"})
        except (User.DoesNotExist, KeyError): #the user does not exist
            return jsonify ({"success" : False, "reason" : "User does not exit"})

@app.route('/logout', methods=['POST'])
def logout():
    key = request.json["key"]
    secret = request.json["secret"]
    try:
        user = User.select().join(APIKey).where(APIKey.key == key, APIKey.secret == secret)
        api_keys = APIKey.delete().where(APIKey.user == user)
        api_keys.execute()
        return jsonify({"success" : True, "key_removed" : True})
    except APIKey.DoesNotExist:
        return jsonify({"success" : True, "key_removed" : False})

@app.route('/join', methods=['POST'])
def join():
    user_to_join = request.json
    user = User(username = user_to_join["username"], email = user_to_join["email"])
    user.set_password(user_to_join["password"])
    user.save()
    return jsonify ({"success" : True})
