from mongoengine import connect

def init_db():
    connect(
        db='areena_match_making_db',
        host='mongodb://localhost/areena_match_making_db',
        uuidRepresentation='standard'
    )
