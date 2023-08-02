from decouple import config
import firebase_admin
from firebase_admin import credentials, db

FB_CRED=str(config('FIREBASE_ADMIN_CRED'))
FB_DB_URL=str(config('FIREBAS_DB_URL'))

cred = credentials.Certificate(FB_CRED)

firebase_admin.initialize_app(cred, {
    'databaseURL': FB_DB_URL
})

ref = db.reference('/')
print(ref.get())
