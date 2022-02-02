mongo -- "$MONGO_INITDB_DATABASE" <<EOF
var user = '$MONGO_INITDB_ROOT_USERNAME';
var passwd = '$MONGO_INITDB_ROOT_PASSWORD';
var admin = db.getSiblingDB('admin');
admin.auth(user, passwd);
db.createUser({user: user, pwd: passwd, roles: ["dbOwner"]});
use $SMARTHUB_MONGO_DATABASE;
db.createUser({ user: "$MONGO_SMARTHUB_USERNAME", pwd: "$MONGO_SMARTHUB_PASSWORD", roles: [ { role: "readWrite", db: "$MONGO_SMARTHUB_DATABASE" } ]});
EOF
